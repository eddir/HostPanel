#!./venv/bin/python3

import sys

from Configuration import Configuration
from watcher import *

VERSION = "4.2"

config = Configuration()


def run_command(command, args):
    # Запуск
    # todo: слишком много аргументов. Придумать способ передавать конфигурацию файлом или запросом.
    # ./client.py start <Master, SR> <server_id> <protocol://domain:port> <watchdog_ port> <health_port> <exe bin path>
    # ./client.py start <Master, SR>
    # ./client.py start
    if command == "start":
        if len(args) >= 6:
            cfg = Configuration(
                package=args[0],
                server_id=args[1],
                panel_address=args[2],
                watchdog_port=args[3],
                health_port=args[4],
                bin_path=' '.join(args[5:]),
            )
            watch(start(cfg))
        elif len(args) == 1:
            watch(start(Configuration(package=args[0])))
        else:
            configuration = Configuration()
            if configuration.package is not None:
                watch(start(configuration))
            else:
                raise ValueError("Configuration.package must be defined")

        return True

    # Остановка
    # ./client.py stop
    elif command == "stop":
        stop(Configuration())
        return True

    # Запуск слежения
    # /start_watcher <Master, SR> <int> <protocol://domain:port>
    elif command == "start_watcher":

        if len(args) == 3:
            watch(Configuration(package=args[0], server_id=args[1], panel_address=args[2]))
        elif len(args) == 1:
            watch(Configuration(package=args[0]))
        else:
            configuration = Configuration()
            if configuration.package is not None:
                watch(configuration)
            else:
                raise ValueError("Configuration.package must be defined")

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
