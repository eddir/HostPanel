import json
import os
import subprocess
import sys
import threading
import traceback
from contextlib import suppress
from datetime import datetime

import psutil
import requests

VERSION = "2.4.7"


def watch(configuration):
    send_status(configuration)
    threading.Timer(60, watch, [configuration]).start()


def send_status(configuration):
    if configuration.package == "Master":
        try:
            with open(os.path.expanduser("~/HostPanel/Master/online.txt"), "r") as json_file:
                online = {"online": json.load(json_file), "server": configuration.server_id}
                requests.post(configuration.panel_address + "/api/servers/online/", verify=False, json=online)

        except IOError:
            pass

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):

        if proc.memory_percent() >= 0.2 or proc.cpu_percent() >= 0.2:
            processes.append({
                'pid': int(proc.pid),
                'name': proc.name(),
                'username': proc.username(),
                'cpu_percent': round(proc.cpu_percent(), 1),
                'memory_percent': round(proc.memory_percent(), 1)
            })

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


def start(configuration):
    """
    Запуск мастера или спавнера

    :param configuration: данные конфигарцаионного файла
    :return: возвращает текущую конфигурацию
    """

    if configuration.server_pid is not None and psutil.pid_exists(configuration.server_pid):
        raise ValueError("Server already running")

    if configuration.package == "Master":
        os.chdir("HostPanel/Master/")
        os.system('chmod +x ' + configuration.bin_path)

        configuration.server_pid = subprocess.Popen(
            configuration.bin_path + " >> ../{0}_master.log"
            .format(datetime.now().strftime("%d.%m_%H:%M")),
            shell=True, preexec_fn=os.setsid).pid

    elif configuration.package == "SR":
        os.chdir("HostPanel/Pack/Spawner/")
        os.system("chmod +x " + configuration.bin_path)
        os.system("chmod +x ~/HostPanel/Pack/Room/Room.x86_64")

        configuration.server_pid = subprocess.Popen(
            configuration.bin_path + " >> ../{0}_spawner.log"
            .format(datetime.now().strftime("%d.%m_%H:%M")),
            shell=True, preexec_fn=os.setsid).pid

    elif configuration.package == "Custom":
        os.chdir("HostPanel/")
        os.system('chmod +x ' + configuration.bin_path)

        configuration.server_pid = subprocess.Popen(
            configuration.bin_path + " >> ../{0}_custom.log"
            .format(datetime.now().strftime("%d.%m_%H:%M")),
            shell=True, preexec_fn=os.setsid).pid

    else:
        raise ValueError("Invalid package " + str(configuration.package))

    return start_watcher(configuration)


def start_watcher(configuration):
    """
    Запоминает PID для управление процессом в будущем

    :param configuration:
    """
    configuration.watcher_pid = os.getpid()
    configuration.save()

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


class Configuration:
    config_path = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../config.txt')

    def __init__(self, server_id=None, panel_address=None, watcher_pid=None, server_pid=None, package=None,
                 bin_path=None):
        """
        Конфигурация микросервиса
        :param server_id: id сервера в панели
        :param panel_address: адрес панели для обращений к API
        :param watcher_pid: id процесса наблюдателя за игровым сервером
        :param server_pid: id процесса игрового сервера
        :param package: тип пакета (Master или Spawner)
        :param bin_path: путь до испольняемого файла
        """
        self.server_id = server_id
        self.panel_address = panel_address
        self.watcher_pid = watcher_pid
        self.server_pid = server_pid
        self.bin_path = bin_path
        self.package = package
        self.load()

    def load(self):
        with suppress(FileNotFoundError):
            with open(self.config_path) as json_file:
                data = json.load(json_file)

            if self.server_id is None:
                self.server_id = data["server_id"]

            if self.panel_address is None:
                self.panel_address = data["panel_address"]

            if self.watcher_pid is None:
                self.watcher_pid = int(data["watcher_pid"])

            if self.server_pid is None:
                self.server_pid = int(data["server_pid"])

            if self.package is None:
                self.package = data["package"]

            if self.bin_path is None:
                self.bin_path = data["bin_path"]

    def save(self):
        with open(self.config_path, 'w') as outfile:
            json.dump({
                'server_id': self.server_id,
                'panel_address': self.panel_address,
                'watcher_pid': self.watcher_pid,
                'server_pid': self.server_pid,
                'package': self.package,
                'bin_path': self.bin_path
            }, outfile)


class ConfigError(Exception):
    pass


config = Configuration()


def run_command(command, args):
    # Запуск
    # /start <Master, SR> <server_id> <protocol://domain:port> <exe bin path>
    if command == "start":
        if len(args) >= 4:
            cfg = Configuration(package=args[0], server_id=args[1], panel_address=args[2], bin_path=' '.join(args[3:]))
            watch(start(cfg))
        elif len(args) == 1:
            watch(start(Configuration(package=args[0])))
        else:
            configuration = Configuration()
            if configuration.package is not None:
                watch(start(configuration))
            else:
                return False

        return True

    # Остановка
    elif command == "stop":
        stop(Configuration())
        return True

    # Запуск слежения
    # /start_watcher <Master, SR> <int> <protocol://domain:port>
    elif command == "start_watcher":

        if len(args) == 3:
            watch(start_watcher(Configuration(package=args[0], server_id=args[1], panel_address=args[2])))
        elif len(args) == 1:
            watch(start_watcher(Configuration(package=args[0])))
        else:
            configuration = Configuration()
            if configuration.package is not None:
                watch(start_watcher(configuration))
            else:
                return False

        return True

    # Остановка слежения
    elif command == "stop_watcher":
        stop_watcher(Configuration())
        return True

    return False


if __name__ == '__main__':

    try:
        if run_command(sys.argv[1], sys.argv[2:]):
            print("Success")
        else:
            print("Incorrect syntax")

    except Exception as e:
        print(str(e), file=sys.stderr)
        print(traceback.format_exc())
