import os
import subprocess
from datetime import datetime
from pathlib import Path

import psutil

from Configuration import ConfigError
from app import run_flask


def watch(configuration):
    configuration.watcher_pid = os.getpid()
    configuration.save()

    run_flask(configuration)


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
