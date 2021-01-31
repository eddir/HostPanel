import json
import os
import subprocess
import sys
import threading

import psutil
import requests

url = 'http://5.180.138.187:8000/api/servers/status/'
path = os.path.dirname(os.path.realpath(__file__))
config_path = path + '/config.txt'


def watch(server):
    threading.Timer(60.0 * 5, watch, [server["id"]]).start()
    send_status(server["id"], server["package"])


def send_status(server_id, package):
    if package == "Master":
        try:
            with open(os.path.expanduser("~/Master/online.txt"), "r") as json_file:
                online = json.load(json_file)
        except IOError:
            online = None
    else:
        online = None

    status = {
        'server': server_id,
        'cpu_usage': int(psutil.cpu_percent()),
        'ram_usage': psutil.virtual_memory().used,
        'ram_available': psutil.virtual_memory().total,
        'hdd_usage': psutil.disk_usage('/').used,
        'hdd_available': psutil.disk_usage('/').total,
        'online': online
    }

    x = requests.post(url, json=status)
    print(x.text)

    return True


def start(package, server_id=None, user=None):
    if server_id is None or user is None:
        try:
            with open(config_path) as json_file:
                data = json.load(json_file)

            server_id = data["server_id"]
            user = data["user"]
        except Exception:
            raise ConfigError("Config is damaged")

    if package == "Master":
        os.system('chmod +x ~/Master/Master.x86_64')
        subprocess.Popen("~/Master/Master.x86_64", shell=True, preexec_fn=os.setsid)
    elif package == "SR":
        os.system('chmod +x ~/Pack/Spawner/Spawner.x86_64')
        subprocess.Popen("~/Pack/Spawner/Spawner.x86_64", shell=True, preexec_fn=os.setsid)
        os.system('chmod +x ~/Pack/Room/Room.x86_64')
    else:
        raise ValueError("Invalid package " + str(package))

    with open(config_path, 'w') as outfile:
        json.dump({
            'server_id': server_id,
            'user': user,
            'pid': os.getpid()
        }, outfile)

    return {
        "id": server_id,
        "package": package
    }


def stop():
    """
    Убивает вотчер и подпроцессы вотчера, а именно запущенные игровые сервера
    :return:
    """
    with open(config_path) as json_file:
        data = json.load(json_file)

    if len(data) > 0 and data['pid']:
        parent = psutil.Process(data['pid'])

        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

    else:
        raise ConfigError("Config is damaged")


class ConfigError(Exception):
    pass


if __name__ == '__main__':

    try:
        # Запуск
        if sys.argv[1] == "start":
            if len(sys.argv) == 5:
                watch(start(package=sys.argv[2], server_id=sys.argv[3], user=sys.argv[4]))
            else:
                watch(start(package=sys.argv[2]))

            print("Success")

        # Остановка
        elif sys.argv[1] == "stop" and len(sys.argv) == 2:
            stop()
            print("Success")

        else:
            raise ValueError("Syntax error")

    except Exception as e:
        print(str(e), file=sys.stderr)
