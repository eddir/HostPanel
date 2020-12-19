import os
import socket
from datetime import datetime
from pprint import pprint
import tarfile

from background_task import background
import paramiko
from paramiko.ssh_exception import AuthenticationException
from django.contrib.auth.models import User

from HostPanel import settings
from panel.models import Server


@background()
def init_server(server_id):
    """
    Подключение к user_root@ip
    Генерация password_single
    Создание user_single
    Загрузка сборки
    Запуск скрипта

    :param server_id:
    :return:
    """
    client = None

    server = Server.objects.get(id=server_id)
    server.password_single = User.objects.make_random_password()
    server.save()

    try:
        print("Подключение...")
        client = ssh_connect(server.ip, server.user_root, server.password_root, server.ssh_key)

        # Создание пользователя
        print("Создание пользователя")
        ssh_command(client, 'sudo useradd -m -d /home/%s -s /bin/bash -c "HostPanel single user" -U %s' %
                    (server.user_single, server.user_single))

        # Настройка окружения
        ssh_command(client, 'sudo sed -i "/^[^#]*PasswordAuthentication[[:space:]]no/c\PasswordAuthentication yes" /etc/ssh/sshd_config')
        ssh_command(client, 'sudo service sshd restart')
        ssh_command(client, 'sudo apt install python3-psutil')

        # Смена пароля пользователя
        stdin, stdout, stderr = ssh_command(client, 'echo "%s:%s" | sudo chpasswd' % (server.user_single, server.password_single))
        client.close()

        # Упаковка файлов
        tar = tarfile.open(settings.MEDIA_ROOT + 'package.tar.gz', "w:gz")
        os.chdir(settings.MEDIA_ROOT + 'package/')
        for name in os.listdir("."):
            tar.add(name)
        tar.close()

        # Погрузка файлов
        print("Загрузка файлов")
        transport = paramiko.Transport((server.ip, 22))
        transport.connect(username=server.user_single, password=server.password_single)
        client = paramiko.SFTPClient.from_transport(transport)
        client.put(settings.MEDIA_ROOT + 'package.tar.gz', '/home/%s/package.tar.gz' % server.user_single)
        client.close()
        os.remove(settings.MEDIA_ROOT + 'package.tar.gz')

        # Анбоксиснг
        print("Распаковка")
        client = ssh_connect(server.ip, server.user_single, server.password_single)
        ssh_command(client, 'tar -xzvf package.tar.gz ')

        print("Запуск клиента...")
        ssh_command(client, 'python3 client.py %s %s &' % (server.id, server.user_single))

        print("Клиент вероятно запущен....")
        server_log(server, "Инициализация сервера.")
        server.save()
        client.close()

        print("Завершено для " + server.name)
    except Exception as e:
        print(str(e))
        server_log(server, str(e))

        if client is not None:
            client.close()


def start_server(server_id):
    server = Server.objects.get(id=server_id)
    client = ssh_connect(server.ip, server.user_single, server.password_single)

    try:
        ssh_command(client, "python3 client.py start &")
        server_log(server, "Запуск мастер сервера.")
    except Exception as e:
        server_log(server, str(e))
        return False


def stop_server(server_id):
    server = Server.objects.get(id=server_id)
    client = ssh_connect(server.ip, server.user_single, server.password_single)

    try:
        stdin, stdout, stderr = ssh_command(client, "python3 client.py stop")
        server_log(server, "Остановка мастер сервера.")
        return stdout
    except Exception as e:
        server_log(server, str(e))
        return False


def server_log(server, message):
    if not server.log:
        server.log = ""

    server.log += "[%s] %s<br>" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
    server.save()


def ssh_connect(hostname, username, password, ssh_key=False, port=22):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if ssh_key:
            client.connect(hostname=hostname, username=username, key_filename=settings.MEDIA_ROOT + 'hostpanel.pem',
                           port=port, timeout=3)
        else:
            client.connect(hostname=hostname, username=username, password=password, port=port, timeout=3)

    except AuthenticationException as e:
        raise Exception("Ошибка авторизации: %s" % str(e))
    except socket.error:
        raise Exception("Сервер не отвечает")

    return client


def ssh_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)

    if stdout.channel.recv_exit_status() != 0:
        raise Exception(stdout.read() + stderr.read())

    return stdin, stdout, stderr


class SFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(SFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise
