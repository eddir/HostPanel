import os
import subprocess
import sys
import threading
import psutil
from pprint import pprint

import requests
import json

url = 'http://5.180.138.187:8000/api/servers/status/'
path = os.path.dirname(os.path.realpath(__file__))
config_path = path + '/config.txt'


def watch(server_id):
    threading.Timer(60.0 * 5, watch, [server_id]).start()
    send_status(server_id)


def send_status(server_id):
    status = {
        'server': server_id,
        'cpu_usage': int(psutil.cpu_percent()),
        'ram_usage': psutil.virtual_memory().used,
        'ram_available': psutil.virtual_memory().total,
        'hdd_usage': psutil.disk_usage('/').used,
        'hdd_available': psutil.disk_usage('/').total
    }

    x = requests.post(url, data=status)

    print(x.text)

    return True


def start(package):
    with open(config_path) as json_file:
        data = json.load(json_file)

    if len(data) > 0:
        server_id = data["server_id"]
        user = data["user"]
    else:
        server_id = sys.argv[1]
        user = sys.argv[2]

    if package == "Master":
        os.system('chmod +x ~/Master/Master.x86_64')
        subprocess.Popen("~/Master/Master.x86_64", shell=True, preexec_fn=os.setsid)
    elif package == "SR":
        os.system('chmod +x ~/Pack/Spawner/Spawner.x86_64')
        subprocess.Popen("~/Pack/Spawner/Spawner.x86_64", shell=True, preexec_fn=os.setsid)
        os.system('chmod +x ~/Pack/Room/Room.x86_64')
        #subprocess.Popen("~/Room/Room.x86_64", shell=True, preexec_fn=os.setsid)
    else:
        print("Invalid package " + str(package))

    with open(config_path, 'w') as outfile:
        json.dump({
            'server_id': server_id,
            'user': user,
            'pid': os.getpid()
        }, outfile)

    return server_id


def stop():
    with open(config_path) as json_file:
        data = json.load(json_file)
    if len(data) > 0 and data['pid']:
        parent = psutil.Process(data['pid'])

        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

        return True

    return False


if __name__ == '__main__':

    if len(sys.argv) == 4:
        print("Started")
        watch(start(sys.argv[3]))

    elif len(sys.argv) == 3 and sys.argv[1] == 'start':
        print("Success") if send_status(start(sys.argv[2])) else print("Config is damaged")

    elif len(sys.argv) == 2 and sys.argv[1] == 'stop':
        print("Success") if stop() else print("Config is damaged")

    else:
        print("Syntax error")
