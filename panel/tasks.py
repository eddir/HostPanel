import os
import shlex
import socket
import sys
import tarfile
from contextlib import suppress
from datetime import datetime

import paramiko
from background_task import background
from django.contrib.auth.models import User
from paramiko import AuthenticationException

from HostPanel import settings
from panel.models import Server, Status, Dedic


class AuthFailedException(Exception):
    pass


class Client:

    def __init__(self, model):
        self.client = None
        self.root_client = None
        self.dedic = model

    def __del__(self):
        self.disconnect(root=True)
        self.disconnect(root=False)

    def connect(self, root=False):
        client = paramiko.SSHClient()
        try:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if root:
                username = self.dedic.user_root
                password = self.dedic.password_root
            else:
                username = self.dedic.user_single
                password = self.dedic.password_single

            if self.dedic.ssh_key:
                key_filename = settings.MEDIA_ROOT + 'hostpanel.pem'
                client.connect(hostname=self.dedic.ip, username=username, port=22, timeout=3, key_filename=key_filename)
            else:
                client.connect(hostname=self.dedic.ip, username=username, password=password, port=22, timeout=3,
                               allow_agent=False, look_for_keys=False)

        except AuthenticationException as e:
            raise AuthFailedException("Ошибка авторизации: %s" % str(e))
        except socket.error as e:
            raise Exception("Сервер не отвечает: %s" % str(e))

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


class DedicUnit(Client):

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        if not self.model.log:
            self.model.log = ""

    def init(self):
        try:
            self.connect()
        except AuthFailedException:
            try:
                self.log("Начинается инициализация пользователя.")

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
                    'sudo service sshd restart && '
                    # Установка пароля
                    'echo "{0}:{1}" | sudo chpasswd && '
                    # Установка зависимостей
                    'sudo apt install -y python3-psutil unzip && '
                    'ufw allow 5000; ufw allow 1500:1600/udp'.format(self.model.user_single,
                                                                     self.model.password_single), root=True)

                self.disconnect(root=True)
                print("Готово")
            except AuthenticationException as e:
                self.log("Ошибка авторизации через root пользователя: " + str(e))
            except Exception as e:
                self.log(str(e))
        except Exception as e:
            self.log(str(e))

    def log(self, message):
        print(message)
        self.model.log += "[%s] %s<br>" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self.model.save()

    def delete(self):
        print("Удаление dedic %d" % self.model.id)

        with suppress(Exception):
            self.command("deluser {0}; rm -rf /home/{0}/".format(self.model.user_single), root=True)

        self.model.delete()


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
        stdin, stdout, stderr = self.command(
            "python3 ~/HostPanel/Caretaker/client.py start {0} {1} {2} >> ~/HostPanel/Caretaker.log &".format(
                package, self.model.id, "http://" + settings.ALLOWED_HOSTS[-1] + ":" + str(settings.PORT)))
        # TODO: другой способ получить адрес для прода
        self.log("Сервер запущен.")
        return stdin, stdout, stderr

    def stop(self):
        stdin, stdout, stderr = self.command("python3 ~/HostPanel/Caretaker/client.py stop")

        self.log("Сервер остановлен.")
        Status(server=self.model, condition=Status.Condition.STOPPED).save()

        return stdin, stdout, stderr

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
        transport = paramiko.Transport((self.model.dedic.ip, 22))
        transport.connect(username=self.model.dedic.user_single, password=self.model.dedic.password_single)
        client = paramiko.SFTPClient.from_transport(transport)

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


@background
def dedic_task(dedic_id, operation):
    """
    Создаёт пользователя в указанной вдс

    :param dedic_id:
    :param operation:
    :return:
    """
    dedic = DedicUnit(Dedic.objects.get(id=dedic_id))

    try:
        if operation == "init":
            dedic.init()
        if operation == "delete":
            dedic.delete()
    except Exception as e:
        dedic.log(str(e))


@background
def server_task(server_id, operation):
    """
    Управляет сервером

    :param server_id:
    :param operation:
    :return:
    """
    server = ServerUnit(Server.objects.get(id=server_id))

    try:
        if operation == "init":
            server.init()
        elif operation == "start":
            server.start()
        elif operation == "update":
            server.update()
        elif operation == "reboot":
            server.reboot()
        elif operation == "update_config":
            server.update_config()
        elif operation == "stop":
            server.stop()

            if server.model.parent is None:
                spawners = Server.objects.filter(parent=server.model.id)
                for spawner in spawners:
                    ServerUnit(spawner).stop()

        elif operation == "delete":
            with suppress(Exception):
                server.stop()
            server.delete()

    except Exception as e:
        print("Для сервера {0}: {1}".format(server_id, str(e)))
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
