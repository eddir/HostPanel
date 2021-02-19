import os
import shlex
import socket
import tarfile
from datetime import datetime

import paramiko
from background_task import background
from django.contrib.auth.models import User
from paramiko import AuthenticationException

from HostPanel import settings
from panel.models import Server, MPackage, SRPackage


class ServerUnit:

    def __init__(self, server):
        self.model = server

        if not self.model.log:
            self.model.log = ""

        self.client = None
        self.root_client = None

    def __del__(self):
        self.disconnect(root=True)
        self.disconnect(root=False)

    def init(self):
        """
        Подключение к user_root@ip
        Генерация password_single
        Создание user_single
        Загрузка сборки
        Запуск скрипта
        """
        self.log("Начинается инициализация сервера.")
        self.model.password_single = User.objects.make_random_password()
        self.model.save()

        print("Подключение...")
        self.connect(root=True)

        # Команды для установки необходимых компонентов и создания пользователя
        print("Настройка VPS")
        self.command(  # Создание пользователя
            'sudo useradd -m -d /home/{0} -s /bin/bash -c "HostPanel single user" -U {0} && '
            # Разрешение на вход в ssh по паролю
            'sudo sed -i "/^[^#]*PasswordAuthentication[[:space:]]no/c\PasswordAuthentication yes" '
            '/etc/ssh/sshd_config && '
            "sudo service sshd restart && "
            # Установка пароля
            'echo "{0}:{1}" | sudo chpasswd && '
            # Установка зависимостей
            "sudo apt install -y python3-psutil unzip".format(self.model.user_single, self.model.password_single),
            root=True)

        self.disconnect(root=True)

        self.upload_package()
        self.upload_config()

        print("Запуск клиента...")
        self.start()

        print("Клиент вероятно запущен....")
        self.log("Инициализация сервера прошла успешно.")

        print("Завершено для " + self.model.name)

    def start(self):
        package = "SR" if self.model.parent else "Master"
        stdin, stdout, stderr = self.command("python3 ~/Caretaker/client.py start {0} {1} {2} &".format(
            package, self.model.id, self.model.user_single)
        )
        self.log("Сервер запущен.")
        return stdin, stdout, stderr

    def stop(self):
        stdin, stdout, stderr = self.command("python3 ~/Caretaker/client.py stop")
        self.log("Сервер остановлен.")
        return stdin, stdout, stderr

    def delete(self):
        print("Удаление сервера %d" % self.model.id)
        self.command("pkill -u {0}; deluser {0}; rm -rf /home/{0}/".format(self.model.user_single), root=True)
        self.model.delete()

    def update(self):
        self.stop()

        if self.model.parent:
            self.command("rm -rf /home/{0}/Caretaker /home/{0}/Spawner/ /home/{0}/Room/".format(self.model.user_single))
        else:
            self.command("rm -rf /home/{0}/Master /home/{0}/Caretaker/".format(self.model.user_single))

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
        transport = paramiko.Transport((self.model.ip, 22))
        transport.connect(username=self.model.user_single, password=self.model.password_single)
        client = paramiko.SFTPClient.from_transport(transport)

        print("package.tar.gz")
        client.put(settings.MEDIA_ROOT + 'Caretaker.tar.gz', '/home/%s/Caretaker.tar.gz' % self.model.user_single)

        if self.model.parent:
            # Зачистка
            self.command("rm -rf /home/{0}/Pack/ && rm -rf /home/{0}/Caretaker/".format(self.model.user_single))

            print("spawner")
            client.put(self.model.package.srpackage.spawner.path,
                       '/home/%s/spawner_package.zip' % self.model.user_single)
            print("room")
            client.put(self.model.package.srpackage.room.path, '/home/%s/room_package.zip' % self.model.user_single)
            unzip = "unzip spawner_package.zip -d /home/{0}/Pack/ && unzip room_package.zip -d /home/{0}/Pack/".format(
                self.model.user_single
            )
            rm = "spawner_package.zip room_package.zip"

        else:
            # Зачистка
            self.command("rm -rf /home/{0}/Master/ && rm -rf /home/{0}/Caretaker/".format(self.model.user_single))

            print("master")
            client.put(self.model.package.mpackage.master.path, '/home/%s/master_package.zip' % self.model.user_single)

            unzip = "unzip master_package.zip -d /home/{0}/".format(self.model.user_single)
            rm = "master_package.zip"

        client.close()
        os.remove(settings.MEDIA_ROOT + 'Caretaker.tar.gz')

        # Анбоксиснг
        print("Распаковка...")
        cmd = """mkdir -p /home/{0}/Caretaker && tar -xzvf Caretaker.tar.gz --directory /home/{0}/Caretaker && {1} && \
              rm Caretaker.tar.gz {2}""".format(self.model.user_single, unzip, rm)
        self.command(cmd, root=False)
        print("Распаковано")

    def update_config(self):
        self.log("Обновление конфига...")
        self.stop()
        self.upload_config()
        self.start()
        self.log("Конфиг обновлён.")

    def upload_config(self):
        path = "~/Pack/Spawner/application.cfg" if self.model.parent else "~/Master/application.cfg"
        content = shlex.quote(self.model.config)
        self.command("echo \"%s\" > %s" % (content, path))

    def log(self, message):
        self.model.log += "[%s] %s<br>" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self.model.save()

    def connect(self, root=False):
        client = paramiko.SSHClient()
        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if root:
                username = self.model.user_root
                password = self.model.password_root
            else:
                username = self.model.user_single
                password = self.model.password_single

            if self.model.ssh_key:
                key_filename = settings.MEDIA_ROOT + 'hostpanel.pem'
                password = None
            else:
                key_filename = None

            client.connect(hostname=self.model.ip, username=username, password=password, port=22, timeout=3,
                           key_filename=key_filename)

        except AuthenticationException as e:
            raise Exception("Ошибка авторизации: %s" % str(e))
        except socket.error:
            raise Exception("Сервер не отвечает")

        if root:
            self.root_client = client
        else:
            self.client = client

    def disconnect(self, root=False):
        if root and self.root_client is not None:
            self.root_client.close()
            self.root_client = None
        elif self.client is not None:
            self.client.close()
            self.client = None

    def command(self, command, root=False):
        client = self.root_client if root else self.client

        if client is None:
            self.connect(root)
            client = self.root_client if root else self.client

        stdin, stdout, stderr = client.exec_command(command)

        if stdout.channel.recv_exit_status() != 0:
            raise Exception(stdout.read() + stderr.read())

        return stdin, stdout, stderr


@background
def server_task(server_id, operation):
    server = ServerUnit(Server.objects.get(id=server_id))

    try:
        if operation == "init":
            server.init()
        elif operation == "start":
            server.start()
        elif operation == "update":
            server.update()
        elif operation == "update_config":
            server.update_config()
        elif operation == "stop":
            server.stop()

            if server.model.parent is None:
                spawners = Server.objects.filter(parent=server.model.id)
                for spawner in spawners:
                    ServerUnit(spawner).stop()

        elif operation == "delete":
            server.stop()
            server.delete()

    except Exception as e:
        print(str(e))
        server.log(str(e))

    del server


@background
def package_task(package_id, operation, package_type):
    try:
        if operation == "install_package":

            if package_type == "master":
                servers = Server.objects.filter(parent=None)
            else:
                servers = Server.objects.exclude(parent=None)

            for server in servers:
                server.package_id = package_id
                server.save()
                server_unit = ServerUnit(server)
                server_unit.log("Обновление сборки (package_id=%d)..." % package_id)
                server_unit.stop()
                server_unit.upload_package()
                server_unit.start()
                server_unit.log("Сборка обновлена.")

    except Exception as e:
        print(str(e))


def get_online():
    raise NotImplemented()
