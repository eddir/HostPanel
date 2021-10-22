import json
import os
import subprocess
import threading
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import sleep

import psutil
import requests

from Configuration import ConfigError
from client import VERSION
from api.app import run_flask


def watch(configuration):
    configuration.watcher_pid = os.getpid()
    configuration.save()

    send_status(configuration)
    threading.Timer(60 * 5, watch, [configuration]).start()
    print(configuration.watchdog_port)
    run_flask(configuration.watchdog_port)


def send_status(configuration):
    if configuration.package == "Master":
        try:
            with open(os.path.expanduser("~/HostPanel/Master/online.txt"), "r") as json_file:
                online = {"online": json.load(json_file), "server": configuration.server_id}
                requests.post(configuration.panel_address + "/api/servers/online/", verify=False, json=online)

        except IOError:
            pass

    processes = get_processes()

    r = requests.post(configuration.panel_address + "/api/v2/servers/status/", verify=False, json={
        'server': configuration.server_id,
        'cpu_usage': int(psutil.cpu_percent()),
        'mem_total': int(psutil.virtual_memory().total / 1024 / 1024),
        'mem_available': int(psutil.virtual_memory().available / 1024 / 1024),
        'disk_total': int(psutil.disk_usage('/').total / 1024 / 1024),
        'disk_available': int(psutil.disk_usage('/').free / 1024 / 1024),
        'processes': json.dumps(processes),
        'caretaker_version': VERSION
    })

    response = r.json()
    if response['code'] != 1:
        print(response['response'])

    return True


def get_processes():
    processes = []
    result = []

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        proc.cpu_percent()
        processes.append(proc)

    sleep(10)

    for proc in processes:

        with suppress(Exception):
            cpu_percent = proc.cpu_percent()
            memory_percent = proc.memory_percent()
            if memory_percent >= 0.2 or cpu_percent >= 0.2:
                result.append({
                    'pid': int(proc.pid),
                    'name': proc.name(),
                    'username': proc.username(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': round(memory_percent, 1),
                    'memory_usage': int(proc.memory_info().rss / 1024 / 1024)
                })

    return result


def start(configuration):
    """
    Запуск мастера или спавнера

    :param configuration:
    :return: возвращает текущую конфигурацию
    """

    if configuration.server_pid is not None and psutil.pid_exists(configuration.server_pid):
        raise ValueError("Server already running")

    if configuration.package == "Master":
        os.chdir(str(Path.home()) + "/HostPanel/Master/")
        os.system('chmod +x ./Master.x86_64')
        configuration.server_pid = subprocess.Popen(
            "./Master.x86_64 >> ../{0}_master.log".format(
                datetime.now().strftime("%d.%m_%H:%M")
            ), shell=True, preexec_fn=os.setsid).pid

    elif configuration.package == "SR":
        os.chdir(str(Path.home()) + "/HostPanel/Pack/Spawner/")
        os.system("chmod +x ./Spawner.x86_64")
        os.system("chmod +x ~/HostPanel/Pack/Room/Room.x86_64")
        configuration.server_pid = subprocess.Popen(
            "./Spawner.x86_64 >> ../{0}_spawner.log".format(
                datetime.now().strftime("%d.%m_%H:%M")
            ), shell=True, preexec_fn=os.setsid).pid

    else:
        raise ValueError("Invalid package " + str(configuration.package))

    return configuration


def stop(configuration):
    """
    Остановить игровой сервер и вотчер
    """
    if configuration.server_pid is not None:
        parent = psutil.Process(configuration.server_pid)

        for child in parent.children(recursive=True):  # todo: а точно recursive?
            child.kill()

        parent.kill()

    else:
        raise ConfigError("Config is damaged")

    stop_watcher(configuration)


def stop_watcher(configuration):
    """
    Останавливает слежение
    """
    if configuration.watcher_pid is not None:
        psutil.Process(configuration.watcher_pid).kill()
