import json
import os
from contextlib import suppress


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
