from contextlib import suppress
from time import sleep

import psutil


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