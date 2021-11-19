from datetime import datetime

from django.contrib.auth.models import User
# noinspection PyProtectedMember
from django.db import close_old_connections
from django.utils import timezone
from paramiko import AuthenticationException

from panel.exceptions import ServerAuthenticationFailed, ServerBadCommand
from panel.tasks.Client import Client


class DedicUnit(Client):

    def __init__(self, model):
        super().__init__(model)
        self.model = model
        if not self.model.log:
            self.model.log = ""

    def init(self):
        """
        Инициализация дедика. Устанавливаются нужные зависимости и создаётся пользователь.

        :return:
        """
        try:
            self.connect()
        except ServerAuthenticationFailed:
            try:
                self.log("Начинается инициализация пользователя.")

                if not self.model.password_single:
                    self.model.password_single = User.objects.make_random_password()
                    self.model.save()

                print("Подключение...")
                self.connect(root=True)

                # Команды для установки необходимых компонентов и создания пользователя
                print("Настройка VPS")

                if self.model.ssh_key:
                    # noinspection PyPep8
                    password_auth = 'sudo sed -i ' \
                                    '"/^[^#]*PasswordAuthentication[[:space:]]no/c\PasswordAuthentication yes" ' \
                                    '/etc/ssh/sshd_config && sudo service sshd restart && sudo service sshd restart && '
                else:
                    password_auth = ""

                self.command((
                    # Создание пользователя
                        'sudo useradd -m -d /home/{0} -s /bin/bash -c "HostPanel single user" -U {0} && ' +

                        # Разрешение на вход в ssh по паролю
                        password_auth +

                        # Установка пароля
                        'echo "{0}:{1}" | sudo chpasswd && '

                        # Решить проблемы со свапом, которые тормозят систему.
                        'grep -qxF "vm.swappiness=0" /etc/sysctl.conf || echo "vm.swappiness=0" >> /etc/sysctl.conf && '

                        # Применить настройки sysctl.conf
                        'sysctl -p && '

                        # Установка зависимостей
                        'sudo apt update && sudo apt install -y python3-virtualenv unzip atop && '

                        # Настройка сети, открытие портов
                        'sudo ufw allow 1500:1600/udp comment "MST spawner" && '
                        'sudo ufw allow 2323,5000,5056/tcp comment "MST master" && '
                        'sudo ufw allow 2323,5000,5056/udp comment "MST master" && '
                        'sudo ufw allow 8000 comment "Watchdog"'

                ).format(
                    self.model.user_single,
                    self.model.password_single
                ), root=True)

                close_old_connections()

                self.disconnect(root=True)
                self.model.condition = True
                self.model.save()
                print("Готово")
            except AuthenticationException as e:
                self.log("Ошибка авторизации через root пользователя: " + str(e))
            except ServerBadCommand as e:
                self.log("Ошибка при выполнении команды: " + str(e))
            except Exception as e:
                self.log(str(e))
        except Exception as e:
            self.log(str(e))

    def log(self, message):
        print("> " + message + " <")
        self.model.log += "[%s] %s<br>" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self.model.save()

    def delete(self, save_model=False):
        print("Удаление dedic %d" % self.model.id)

        try:
            self.command("pkill -u {0}; deluser {0}; rm -rf /home/{0}/".format(self.model.user_single), root=True)
        except Exception as e:
            print(str(e))

        if not save_model:
            self.model.delete()

    def reconnect(self):
        print("Попытка переподключиться к dedic %d" % self.model.id)

        try:
            self.connect()
            self.model.condition = True
        except Exception as e:
            self.model.log += "[%s] %s<br>" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(e))
            self.model.condition = False

        self.model.last_listen = timezone.now()
        self.model.save()
