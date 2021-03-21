import socket

import paramiko
from paramiko import AuthenticationException

from HostPanel import settings
from panel.exceptions import ServerAuthenticationFailed, ServerBadCommand


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
        out = stdout.readlines()
        err = stderr.readlines()

        if stdout.channel.recv_exit_status() != 0:
            raise ServerBadCommand(' '.join(err))

        return out, err
