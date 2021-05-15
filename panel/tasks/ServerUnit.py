import os
import shlex
import tarfile
from datetime import datetime

from HostPanel import settings
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
        self.log("&2Сервер запущен.")

    def stop(self):
        self.command("python3 ~/HostPanel/Caretaker/client.py stop")

        self.log("Сервер остановлен.")
        Status(server=self.model, condition=Status.Condition.STOPPED).save()

    def start_watcher(self):
        """
        Запустить скрипт отслеживания
        """
        self.command("python3 ~/HostPanel/Caretaker/client.py start_watcher &")
        self.log("Отслеживание возобновлено.")

    def stop_watcher(self):
        """
        Остановить работу скрипта без остановки игрового сервера
        """
        self.command("python3 ~/HostPanel/Caretaker/client.py stop_watcher")
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
        self.command("rm -rf /home/{0}/HostPanel/".format(self.model.dedic.user_single))

        self.upload_package()
        self.log("Сервер обновлён успешно.")

    def upload_package(self):

        # Погрузка архивов M и SR
        print("Загрузка файлов")
        client = self.get_sftp_client()

        if self.model.parent:
            # Зачистка
            self.command("rm -rf /home/{0}/HostPanel/Pack/ && rm -rf /home/{0}/HostPanel/Caretaker/ "
                         "&& mkdir -p /home/{0}/HostPanel".format(self.model.dedic.user_single))
            print("spawner")
            client.put(self.model.package.srpackage.spawner.path,
                       '/home/%s/HostPanel/spawner_package.zip' % self.model.dedic.user_single)
            print("room")
            client.put(self.model.package.srpackage.room.path, '/home/%s/HostPanel/room_package.zip' %
                       self.model.dedic.user_single)
            unzip = "unzip ~/HostPanel/spawner_package.zip -d /home/{0}/HostPanel/Pack/ && " \
                    "unzip ~/HostPanel/room_package.zip -d /home/{0}/HostPanel/Pack/"\
                .format(self.model.dedic.user_single)
            rm = "~/HostPanel/spawner_package.zip ~/HostPanel/room_package.zip"

        else:
            # Зачистка
            cmd = "rm -rf /home/{0}/HostPanel/Master/ && rm -rf /home/{0}/HostPanel/Caretaker/ && " \
                  "mkdir -p /home/{0}/HostPanel"
            self.command(cmd.format(self.model.dedic.user_single))

            print("master")
            client.put(self.model.package.mpackage.master.path, '/home/{0}/HostPanel/master_package.zip'.format(
                self.model.dedic.user_single))

            unzip = "unzip ~/HostPanel/master_package.zip -d /home/{0}/HostPanel/".format(self.model.dedic.user_single)
            rm = "~/HostPanel/master_package.zip"

        self.upload_caretaker()

        self.disconnect(sftp=True)

        # Анбоксиснг
        print("Распаковка...")
        cmd = """mkdir -p /home/{0}/HostPanel/Caretaker && \
            {1} && rm ~/HostPanel/Caretaker.tar.gz {2}""".format(self.model.dedic.user_single, unzip, rm)
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
        self.log("&eНачинается обновление Caretaker...")
        self.stop_watcher()
        self.command("rm -rf ~/HostPanel/Caretaker")
        self.upload_caretaker()
        self.start_watcher()
        self.log("&eОбновление Caretaker завершено")

    def update_caretaker_legacy(self):
        self.log("&eНачинается обновление Caretaker...")

        is_running = self.model.is_running()

        if is_running:
            self.stop()

        self.command("rm -rf ~/HostPanel/Caretaker")
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
        tar = tarfile.open(settings.MEDIA_ROOT + 'Caretaker.tar.gz', "w:gz")
        os.chdir(settings.MEDIA_ROOT + 'Caretaker/')

        for name in os.listdir("."):
            tar.add(name)
        tar.close()

        print("package.tar.gz")
        self.command("mkdir -p /home/{0}/HostPanel/Caretaker".format(self.model.dedic.user_single))
        client.put(settings.MEDIA_ROOT + 'Caretaker.tar.gz', '/home/%s/HostPanel/Caretaker.tar.gz'
                   % self.model.dedic.user_single)

        self.command("tar -xzvf /home/{0}/HostPanel/Caretaker.tar.gz --directory /home/{0}/HostPanel/Caretaker".format(
            self.model.dedic.user_single
        ))

        os.remove(settings.MEDIA_ROOT + 'Caretaker.tar.gz')

    def warning(self, message):
        self.log("&e" + message)

    def log(self, message):
        self.model.log += "[%s] %s<br>" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self.model.save()
