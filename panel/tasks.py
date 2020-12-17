import os
import socket
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

    print("Подключение...")

    server = Server.objects.get(id=server_id)
    server.password_single = User.objects.make_random_password()
    server.save()

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=server.ip, username=server.user_root, password=server.password_root, port=22,
                       timeout=10)
    except AuthenticationException:
        print("Ошибка авторизации")
    except socket.error:
        print("Сервер не отвечает")
    except:
        print("Неизвестная проблема")
        return

        # Создание пользователя
    stdin, stdout, stderr = client.exec_command(
        'sudo useradd -m -d /home/%s -s /bin/bash -c "HostPanel single user" -U %s'
        % (server.user_single, server.user_single))
    if stdout.channel.recv_exit_status() != 0:
        raise Exception(stdout.read() + stderr.read())

    # Настройка окружения
    stdin, stdout, stderr = client.exec_command('sudo apt install python3-psutil')
    if stdout.channel.recv_exit_status() != 0:
        raise Exception(stdout.read() + stderr.read())

    # Смена пароля пользователя
    stdin, stdout, stderr = client.exec_command('echo "%s:%s" | sudo chpasswd' %
                                                (server.user_single, server.password_single))
    if stdout.channel.recv_exit_status() != 0:
        raise Exception(stdout.read() + stderr.read())

    client.close()

    print("Загрузка файлов")

    # Упаковка файлов
    tar = tarfile.open(settings.MEDIA_ROOT + 'package.tar.gz', "w:gz")
    os.chdir(settings.MEDIA_ROOT + 'package/')
    for name in os.listdir("."):
        tar.add(name)
    tar.close()

    # Погрузка файлов
    transport = paramiko.Transport((server.ip, 22))
    transport.connect(username=server.user_single, password=server.password_single)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(settings.MEDIA_ROOT + 'package.tar.gz', '/home/%s/package.tar.gz' % server.user_single)
    sftp.close()
    os.remove(settings.MEDIA_ROOT + 'package.tar.gz')

    client.connect(hostname=server.ip, username=server.user_single, password=server.password_single, port=22)

    # Анбоксиснг
    stdin, stdout, stderr = client.exec_command('tar -xzvf package.tar.gz ')
    if stdout.channel.recv_exit_status() != 0:
        raise Exception(stdout.read() + stderr.read())

    print("Запуск клиента...")

    stdin, stdout, stderr = client.exec_command(('python3 client.py %s %s &' % (server.id, server.user_single)))

    print("Клиент вероятно запущен....")

    client.close()

    print("Завершено для " + server.name)


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
