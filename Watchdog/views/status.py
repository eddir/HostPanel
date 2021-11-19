import getpass

# todo: в проде это работает без ошибок. Здесь в IDEA почему не так?
# надо создать отдельный проект в IDEA, а здесь папку заигнорить, чтобы ошибок не было ложных
import json

import psutil
from views.logs import get_health

from utils import get_processes


def status():
    """
    Возвращает состояние сервере
    :return:
    """
    if get_health(1555):
        return {
            'code': 0,
            'response': "ok"
        }
    else:
        return {
            'code': 1,
            'response': "Something goes wrong"
        }


def stat():
    """
    Возвращает статистику сервера в реальном времени
    :return:
    """
    processes = get_processes()
    return {
        'code': 0,
        'response': {
            'cpu_usage': int(psutil.cpu_percent()),
            'mem_total': int(psutil.virtual_memory().total / 1024 / 1024),
            'mem_available': int(psutil.virtual_memory().available / 1024 / 1024),
            'disk_total': int(psutil.disk_usage('/').total / 1024 / 1024),
            'disk_available': int(psutil.disk_usage('/').free / 1024 / 1024),
            'processes': json.dumps(processes),
            "caretaker_version": "4.0.1"  # todo: import
        }
    }


def ping():
    return {
        'user': str(getpass.getuser()),
        'version': "1.0"
    }
