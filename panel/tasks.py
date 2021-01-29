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
from panel.models import Server


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
        package = "Master" if self.model.m_package else "SR"
        stdin, stdout, stderr = self.command("python3 ~/Caretaker/client.py start {0} {1} {2} &".format(
            package, self.model.id, self.model.user_single))
        self.log("Сервер запущен.")
        return stdin, stdout, stderr

    def stop(self):
        stdin, stdout, stderr = self.command("python3 ~/Caretaker/client.py stop")
        self.log("Сервер остановлен.")
        return stdin, stdout, stderr

    def update(self):
        self.stop()

        if self.model.m_package:
            self.command("rm -rf /home/{0}/Master /home/{0}/Caretaker/".format(self.model.user_single))
        elif self.model.sr_package:
            self.command("rm -rf /home/{0}/Caretaker /home/{0}/Spawner/ /home/{0}/Room/".format(self.model.user_single))

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

        if self.model.m_package:
            print("master")
            client.put(self.model.m_package.master.path, '/home/%s/master_package.zip' % self.model.user_single)

            unzip = "unzip master_package.zip -d /home/{0}/ && "
            rm = "master_package.zip"

        elif self.model.sr_package:
            print("spawner")
            client.put(self.model.sr_package.spawner.path, '/home/%s/spawner_package.zip' % self.model.user_single)
            print("room")
            client.put(self.model.sr_package.room.path, '/home/%s/room_package.zip' % self.model.user_single)

            unzip = "unzip spawner_package.zip -d /home/{0}/Pack/ && unzip room_package.zip -d /home/{0}/Pack/ && "
            rm = "spawner_package.zip room_package.zip"
        else:
            client.close()
            raise Exception("Не найдена ни одна сборка для сервера #" + str(self.model.id))

        client.close()
        os.remove(settings.MEDIA_ROOT + 'Caretaker.tar.gz')

        # Анбоксиснг
        print("Распаковка")
        self.command(("mkdir -p /home/{0}/Caretaker && tar -xzvf Caretaker.tar.gz --directory /home/{0}/Caretaker && "
                      + unzip + "rm Caretaker.tar.gz " + rm).format(self.model.user_single), root=False)

    def update_config(self):
        self.log("Обновление конфига...")
        self.stop()
        self.upload_config()
        self.start()
        self.log("Конфиг обновлён.")

    def upload_config(self):
        path = "~/Master/application.cfg" if self.model.m_package else "~/Pack/Spawner/application.cfg"
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
        elif operation == "stop":
            server.stop()
        elif operation == "update":
            server.update()
        elif operation == "update_config":
            server.update_config()

    except Exception as e:
        print(str(e))
        server.log(str(e))

    del server


def get_online():
    raise NotImplemented()
