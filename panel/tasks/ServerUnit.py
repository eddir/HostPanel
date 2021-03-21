import os
import shlex
import tarfile
from datetime import datetime

import paramiko
from paramiko import AuthenticationException

from HostPanel import settings
from panel.exceptions import ServerAuthenticationFailed
from panel.models import Status
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
        self.upload_config()

        print("Запуск клиента...")
        self.start()

        print("Клиент вероятно запущен....")
        self.log("Инициализация сервера прошла успешно.")

        print("Завершено для " + self.model.name)

    def start(self):
        package = "SR" if self.model.parent else "Master"
        self.command(
            "python3 ~/HostPanel/Caretaker/client.py start {0} {1} {2} >> ~/HostPanel/Caretaker.log &".format(
                package, self.model.id, "http://" + settings.ALLOWED_HOSTS[-1] + ":" + str(settings.PORT)))
        # TODO: другой способ получить адрес для прода
        self.log("Сервер запущен.")

    def stop(self):
        self.command("python3 ~/HostPanel/Caretaker/client.py stop")

        self.log("Сервер остановлен.")
        Status(server=self.model, condition=Status.Condition.STOPPED).save()

    def reboot(self):
        self.log("Reboot")
        Status(server=self.model, condition=Status.Condition.REBOOT).save()

        self.command("reboot", root=True)

    def delete(self):
        print("Удаление сервера %d" % self.model.id)
        Status(server=self.model, condition=Status.Condition.DELETED).save()

        self.command("rm -rf /home/{0}/HostPanel/".format(self.model.dedic.user_single), root=True)
        self.model.delete()

    def update(self):
        self.stop()
        self.command("rm -rf /home/{0}/HostPanel/".format(self.model.dedic.user_single))

        self.upload_package()
        self.start()
        self.log("Сервер обновлён успешно.")

    def upload_package(self):
        # Упаковка файлов
        tar = tarfile.open(settings.MEDIA_ROOT + 'Caretaker.tar.gz', "w:gz")
        os.chdir(settings.MEDIA_ROOT + 'Caretaker/')

        for name in os.listdir("."):
            tar.add(name)
        tar.close()

        # Погрузка архивов M и SR
        print("Загрузка файлов")

        try:
            transport = paramiko.Transport((self.model.dedic.ip, 22))
            transport.connect(username=self.model.dedic.user_single, password=self.model.dedic.password_single)
            client = paramiko.SFTPClient.from_transport(transport)
        except AuthenticationException:
            raise ServerAuthenticationFailed("Не удалось подключиться к {0}@{1} . Ошибка при авторизации.".format(
                self.model.dedic.user_single, self.model.dedic.ip
            ))

        print("package.tar.gz")
        self.command("mkdir -p /home/{0}/HostPanel/Caretaker".format(self.model.dedic.user_single))
        client.put(settings.MEDIA_ROOT + 'Caretaker.tar.gz', '/home/%s/HostPanel/Caretaker.tar.gz'
                   % self.model.dedic.user_single)

        if self.model.parent:
            # Зачистка
            self.command("rm -rf /home/{0}/HostPanel/Pack/ && rm -rf /home/{0}/HostPanel/Caretaker/".format(
                self.model.dedic.user_single))
            print("spawner")
            client.put(self.model.package.srpackage.spawner.path,
                       '/home/%s/HostPanel/spawner_package.zip' % self.model.dedic.user_single)
            print("room")
            client.put(self.model.package.srpackage.room.path, '/home/%s/HostPanel/room_package.zip' %
                       self.model.dedic.user_single)
            unzip = "unzip ~/HostPanel/spawner_package.zip -d /home/{0}/HostPanel/Pack/ && " \
                    "unzip ~/HostPanel/room_package.zip -d /home/{0}/HostPanel/Pack/".format(
                self.model.dedic.user_single)
            rm = "~/HostPanel/spawner_package.zip ~/HostPanel/room_package.zip"

        else:
            # Зачистка
            self.command("rm -rf /home/{0}/HostPanel/Master/ && rm -rf /home/{0}/HostPanel/Caretaker/".format(
                self.model.dedic.user_single))
            print("master")
            client.put(self.model.package.mpackage.master.path, '/home/%s/HostPanel/master_package.zip'
                       % self.model.dedic.user_single)

            unzip = "unzip ~/HostPanel/master_package.zip -d /home/{0}/HostPanel/".format(self.model.dedic.user_single)
            rm = "~/HostPanel/master_package.zip"

        client.close()
        os.remove(settings.MEDIA_ROOT + 'Caretaker.tar.gz')

        # Анбоксиснг
        print("Распаковка...")
        cmd = """mkdir -p /home/{0}/HostPanel/Caretaker && \
            tar -xzvf ~/HostPanel/Caretaker.tar.gz --directory /home/{0}/HostPanel/Caretaker && \
            {1} && rm ~/HostPanel/Caretaker.tar.gz {2}""".format(self.model.dedic.user_single, unzip, rm)
        self.command(cmd, root=False)
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

    def log(self, message):
        self.model.log += "[%s] %s<br>" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self.model.save()
