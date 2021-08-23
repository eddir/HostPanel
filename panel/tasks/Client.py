import socket

import paramiko
from paramiko import AuthenticationException

from HostPanel import settings
from panel.exceptions import ServerAuthenticationFailed, ServerBadCommand


class Client:

    def __init__(self, model):
        self.client = None
        self.root_client = None
        self.sftp_client = None
        self.dedic = model

    def __del__(self):
        self.disconnect(root=True, single=True, sftp=True)

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

        except AuthenticationException:
            self.dedic.condition = False
            self.dedic.save()
            raise ServerAuthenticationFailed("Не удалось подключиться к {0}@{1} . Ошибка при авторизации.".format(
                self.dedic.user_single, self.dedic.ip
            ))
        except socket.error as e:
            self.dedic.condition = False
            self.dedic.save()
            raise Exception("Сервер не отвечает: %s" % str(e))

        if root:
            self.root_client = client
        else:
            self.client = client

    def disconnect(self, root=False, single=False, sftp=False):
        """
        Закрываем все соединения, чтобы не висели в памяти

        :param sftp: отключиться от клиента SFTP
        :param single: отключиться от SSH клиента под обычным пользователем
        :param root: отключиться от SSH клиента под рут пользователем
        :return:
        """
        if root and self.root_client is not None:
            self.root_client.close()
            self.root_client = None
        if single and self.client is not None:
            self.client.close()
            self.client = None
        if sftp and self.sftp_client is not None:
            self.sftp_client.close()
            self.sftp_client = None

    def command(self, command, root=False, output=False):
        """
        Выполнить команду по SSH
        :param command: текст команды
        :param root: нужно ли выполнить команду от имени рут пользователя
        :param output: нужно ли возвращать результат выполнения команды
        :return:
        """
        client = self.root_client if root else self.client

        if client is None:
            self.connect(root)
            client = self.root_client if root else self.client

        try:
            stdin, stdout, stderr = client.exec_command(command)
        except paramiko.ssh_exception.SSHException:
            # Вызвается при утрате соединения
            self.connect()
            client = self.root_client if root else self.client
            stdin, stdout, stderr = client.exec_command(command)

        if stdout.channel.recv_exit_status() != 0:
            err = stderr.readlines()
            raise ServerBadCommand("Статус " + str(stdout.channel.recv_exit_status()) + ": " + ' '.join(err))

        return stdout.readlines() if output else None

    def get_sftp_client(self):
        if self.sftp_client is None:
            try:
                transport = paramiko.Transport((self.dedic.ip, 22))
                transport.connect(username=self.dedic.user_single, password=self.dedic.password_single)
                self.sftp_client = paramiko.SFTPClient.from_transport(transport)
            except AuthenticationException:
                raise ServerAuthenticationFailed("Не удалось подключиться к {0}@{1} . Ошибка при авторизации.".format(
                    self.dedic.user_single, self.dedic.ip
                ))
        return self.sftp_client
