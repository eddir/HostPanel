import json
import os
import subprocess
import threading
from datetime import datetime

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
    run_flask()


def send_status(configuration):
    if configuration.package == "Master":
        try:
            with open(os.path.expanduser("~/HostPanel/Master/online.txt"), "r") as json_file:
                online = {"online": json.load(json_file), "server": configuration.server_id}
                requests.post(configuration.panel_address + "/api/servers/online/", verify=False, json=online)

        except IOError:
            pass

    r = requests.post(configuration.panel_address + "/api/servers/status/", verify=False, json={
        'server': configuration.server_id,
        'cpu_usage': int(psutil.cpu_percent()),
        'ram_usage': psutil.virtual_memory().used,
        'ram_available': psutil.virtual_memory().total,
        'hdd_usage': psutil.disk_usage('/').used,
        'hdd_available': psutil.disk_usage('/').total,
        'caretaker_version': VERSION
    })

    print(r.text)

    return True


def start(configuration):
    """
    Запуск мастера или спавнера

    :param configuration:
    :return: возвращает текущую конфигурацию
    """

    if configuration.server_pid is not None and psutil.pid_exists(configuration.server_pid):
        raise ValueError("Server already running")

    if configuration.package == "Master":
        os.chdir("HostPanel/Master/")
        os.system('chmod +x ./Master.x86_64')
        configuration.server_pid = subprocess.Popen(
            "./Master.x86_64 >> ../{0}_master.log".format(
                datetime.now().strftime("%d.%m_%H:%M")
            ), shell=True, preexec_fn=os.setsid).pid

    elif configuration.package == "SR":
        os.chdir("HostPanel/Pack/Spawner/")
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
