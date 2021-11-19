import os
import shlex
import tarfile
from contextlib import suppress
from datetime import datetime

# noinspection PyProtectedMember
import requests
from background_task.models import Task
# noinspection PyProtectedMember
from django.db import close_old_connections
from django.utils import timezone

from HostPanel import settings
from panel.exceptions import ServerBadCommand
from panel.models import Status, Server
from panel.serializers import StatusSerializer
from panel.tasks import tasks
from panel.tasks.Client import Client


class ServerUnit(Client):

    def __init__(self, server):
        super().__init__(server.dedic)
        self.model = server

        if not self.model.log:
            self.model.log = ""

    def init(self):
        """
        Загрузка сборки
        Запуск скрипта
        """
        self.log("Начинается инициализация сервера.")

        self.upload_package()

        self.command("ufw allow {0} comment 'watchdog web flask'".format(self.model.watchdog_port), root=True)

        print("Запуск клиента...")
        self.start()

        print("Клиент вероятно запущен....")
        self.log("Инициализация сервера прошла успешно.")

        print("Завершено для " + self.model.name)

    def start(self):
        if self.model.custom:
            package = "Custom"
            bin_path = self.model.package.cpackage.bin_path
        elif self.model.parent:
            package = "SR"
            bin_path = self.model.package.srpackage.bin_path
        else:
            package = "Master"
            bin_path = self.model.package.mpackage.bin_path

        # REVERSE_DNS извлекается из локальных настроек
        # noinspection PyUnresolvedReferences
        cmd = \
            "cd ~/HostPanel/watchdog/ && ./client.py start {0} {1} {2} {3} {4} >> ~/HostPanel/watchdog.log &".format(
                package,
                self.model.id,
                settings.REVERSE_DNS,
                self.model.watchdog_port,
                bin_path
            )
        print(cmd)
        self.command(cmd)
        # создать задачу с повторением каждую минуту на self.monitor
        tasks.server_task(self.model.id, "monitor", repeat=60)
        tasks.server_task(self.model.id, "stat", repeat=60*10)
        self.log("&2Сервер запущен.")

    def stop(self):
        self.command("cd ~/HostPanel/watchdog/ && ./client.py stop")

        self.log("Сервер остановлен.")
        Status(server=self.model, condition=Status.Condition.STOPPED).save()
        Task.objects.filter(task_name="panel.tasks.tasks.server_task").filter(
            task_params__contains=self.model.id).delete()

    def start_watcher(self):
        """
        Запустить скрипт отслеживания
        """
        print("cd ~/HostPanel/watchdog/ && ./client.py start_watcher &")
        self.command("cd ~/HostPanel/watchdog/ && ./client.py start_watcher >> ~/HostPanel/watchdog.log &")
        print("All right")
        self.log("Отслеживание возобновлено.")

    def stop_watcher(self):
        """
        Остановить работу скрипта без остановки игрового сервера
        """
        self.command("cd ~/HostPanel/watchdog/ && ./client.py stop_watcher")
        self.log("Отслеживание приостановлено.")

    def reboot(self):
        self.log("Reboot")
        Status(server=self.model, condition=Status.Condition.REBOOT).save()

        self.command("reboot", root=True)

    def delete(self, save_model=False):
        print("Удаление сервера %d" % self.model.id)
        Status(server=self.model, condition=Status.Condition.DELETED).save()

        self.command("rm -rf /home/{0}/HostPanel/".format(self.model.dedic.user_single), root=True)

        if not save_model:
            self.model.delete()

    def update(self):
        self.stop()
        self.command("rm -rf /home/{0}/HostPanel/".format(self.model.dedic.user_single))  # todo: это обязательно?

        self.upload_package()
        self.log("Сервер обновлён успешно.")

    def upload_package(self):
        """
        Очищает рабочую область, загружает сборку, распаковывает, устанавливает watchdog и конфиг.
        """

        # Погрузка архивов M и SR
        print("Загрузка файлов")
        client = self.get_sftp_client()

        if self.model.custom:
            # Зачистка
            cmd = "rm -rf /home/{0}/HostPanel/Custom/ && rm -rf /home/{0}/HostPanel/watchdog/ && " \
                  "mkdir -p /home/{0}/HostPanel"
            self.command(cmd.format(self.model.dedic.user_single))

            print("custom")
            client.put(self.model.package.cpackage.archive.path,
                       '/home/{0}/HostPanel/custom_package.zip'.format(self.model.dedic.user_single))

            unzip = "unzip -n ~/HostPanel/custom_package.zip -d /home/{0}/HostPanel/".format(
                self.model.dedic.user_single)
            rm = "~/HostPanel/custom_package.zip"
        elif self.model.parent:
            # Зачистка
            self.command("rm -rf /home/{0}/HostPanel/Pack/ && rm -rf /home/{0}/HostPanel/watchdog/ "
                         "&& mkdir -p /home/{0}/HostPanel".format(self.model.dedic.user_single))
            print("spawner")
            client.put(self.model.package.srpackage.spawner.path,
                       '/home/%s/HostPanel/spawner_package.zip' % self.model.dedic.user_single)
            print("room")
            client.put(self.model.package.srpackage.room.path, '/home/%s/HostPanel/room_package.zip' %
                       self.model.dedic.user_single)
            unzip = "unzip -n ~/HostPanel/spawner_package.zip -d /home/{0}/HostPanel/Pack/ && " \
                    "unzip -n ~/HostPanel/room_package.zip -d /home/{0}/HostPanel/Pack/" \
                .format(self.model.dedic.user_single)
            rm = "~/HostPanel/spawner_package.zip ~/HostPanel/room_package.zip"

        else:
            # Зачистка
            cmd = "rm -rf /home/{0}/HostPanel/Master/ && rm -rf /home/{0}/HostPanel/watchdog/ && " \
                  "mkdir -p /home/{0}/HostPanel"
            self.command(cmd.format(self.model.dedic.user_single))

            print("master")
            client.put(self.model.package.mpackage.master.path, '/home/{0}/HostPanel/master_package.zip'.format(
                self.model.dedic.user_single))

            unzip = "unzip -n ~/HostPanel/master_package.zip -d /home/{0}/HostPanel/".format(
                self.model.dedic.user_single)
            rm = "~/HostPanel/master_package.zip"

        close_old_connections()

        self.upload_caretaker()
        self.disconnect(sftp=True)

        cmd = """mkdir -p /home/{0}/HostPanel/watchdog && \
            {1} && rm ~/HostPanel/watchdog.tar.gz {2}""".format(self.model.dedic.user_single, unzip, rm)
        self.command(cmd, root=False)
        self.upload_config()
        print("Распаковано")

    def update_config(self):
        self.log("Обновление конфига...")
        self.stop()
        self.upload_config()
        self.start()
        self.log("Конфиг обновлён.")

    def upload_config(self):
        path = "~/HostPanel/Pack/Spawner/application.cfg" if self.model.parent else "~/HostPanel/Master/application.cfg"
        content = shlex.quote(self.model.config)
        self.command("echo %s > %s" % (content, path))

    def update_caretaker(self):
        self.log("&eНачинается обновление watchdog...")

        try:
            self.stop_watcher()
        except ServerBadCommand:
            pass

        self.command("rm -rf ~/HostPanel/watchdog")
        self.upload_caretaker()
        self.start_watcher()
        self.log("&eОбновление watchdog завершено")

    def update_caretaker_legacy(self):
        self.log("&eНачинается обновление watchdog...")

        is_running = self.model.is_running()

        if is_running:
            self.stop()

        self.command("rm -rf ~/HostPanel/watchdog")
        self.upload_caretaker()

        if is_running:
            self.start()

        self.log("&eОбновление завершено")
        pass

    def upload_caretaker(self):
        """
        Установка управляющего скрипта

        :return:
        """
        client = self.get_sftp_client()
        # Упаковка файлов
        tar = tarfile.open(settings.MEDIA_ROOT + 'watchdog.tar.gz', "w:gz")
        os.chdir(str(settings.BASE_DIR) + '/watchdog/')

        for name in os.listdir("."):
            tar.add(name)
        tar.close()

        print("Загрузка package.tar.gz для обновления скрипта")
        self.command("mkdir -p /home/{0}/HostPanel/watchdog".format(self.model.dedic.user_single))
        client.put(settings.MEDIA_ROOT + 'watchdog.tar.gz', '/home/%s/HostPanel/watchdog.tar.gz'
                   % self.model.dedic.user_single)

        # Распаковка
        self.command("tar -xzvf /home/{0}/HostPanel/watchdog.tar.gz --directory /home/{0}/HostPanel/watchdog".format(
            self.model.dedic.user_single
        ))

        print("Установка virtualenv")
        self.command("cd /home/{0}/HostPanel/watchdog/ && virtualenv venv".format(
            self.model.dedic.user_single
        ), debug=True)

        print("Установка зависимостей")
        self.command("cd /home/{0}/HostPanel/watchdog/ && "
                     "chmod +x client.py && "
                     "source ./venv/bin/activate && "
                     "pip install -r requirements.txt && "
                     "deactivate".format(self.model.dedic.user_single))

        os.remove(settings.MEDIA_ROOT + 'watchdog.tar.gz')

    def monitor(self):
        with suppress(Exception):
            print('http://{}:{}/status/'.format(self.model.dedic.ip, self.model.watchdog_port))
            req = requests.get('http://{}:{}/status/'.format(self.model.dedic.ip, self.model.watchdog_port))
            if req.json()['code'] == 0:
                self.log("Monitor ok")
                return

        self.log("Monitor failed")

    def retrieve_stat(self):
        with suppress(Exception):
            req = requests.get('http://{}:{}/stat/'.format(self.model.dedic.ip, self.model.watchdog_port))
            if req.json()['code'] == 0:
                data = req.json()['response']
                stat = {
                    'server': self.model.id,

                    'cpu_usage': data['cpu_usage'],

                    'mem_total': data['mem_total'],
                    'mem_available': data['mem_available'],

                    'disk_total': data['disk_total'],
                    'disk_available': data['disk_available'],
                }
                serializer = StatusSerializer(data=stat)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

                server = Server.objects.get(id=data['server'])
                server.dedic.last_listen = timezone.now()
                server.dedic.connection = True
                server.dedic.save()

                server.processes = data['processes']
                server.save()

    def warning(self, message):
        self.log("&e" + message)

    def log(self, message):
        self.model.log += "[%s] %s<br>" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self.model.save()
