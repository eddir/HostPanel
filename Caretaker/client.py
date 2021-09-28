import sys

from Configuration import Configuration
from watcher import *

VERSION = "3.0.0.1"

config = Configuration()


def run_command(command, args):
    # Запуск
    # /start <Master, SR> <int> <protocol://domain:port>
    if command == "start":
        if len(args) == 3:
            # fixme: где bin path?
            watch(start(Configuration(package=args[0], server_id=args[1], panel_address=args[2])))
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
