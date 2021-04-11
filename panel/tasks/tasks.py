import traceback
from contextlib import suppress
from pprint import pprint

from background_task import background

from panel.models import Server, Dedic
from panel.tasks.DedicUnit import DedicUnit
from panel.tasks.ServerUnit import ServerUnit


@background
def dedic_task(dedic_id, operation):
    """
    Создаёт пользователя в указанной вдс
    :param dedic_id:
    :param operation:
    :return:
    """

    # Fix temporary (2006, 'MySQL server has gone away')
    from django.db import close_old_connections
    close_old_connections()

    dedic = DedicUnit(Dedic.objects.get(id=dedic_id))

    try:
        if operation == "init":
            dedic.init()
        if operation == "delete":
            dedic.delete()
        if operation == "reconnect":
            dedic.reconnect()
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

    # Fix temporary (2006, 'MySQL server has gone away')
    from django.db import close_old_connections
    close_old_connections()

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

        elif operation == "reinstall":
            server.log("Переустановка...")
            with suppress(Exception):
                server.stop()
            server.delete(save_model=True)

            server2 = None
            query = Server.objects.filter(dedic=server.dedic).exclude(id=server_id)
            if query.exists():
                server2 = ServerUnit(query.get())
                server2.log("Переустановка...")
                with suppress(Exception):
                    server2.stop()
                server2.delete(save_model=True)

            dedic = DedicUnit(server.model.dedic)
            dedic.delete(save_model=True)
            dedic.init()

            if server2:
                server2.init()
                server2.log("Переустановка завершена.")

            server.init()
            server.log("Переустановка завершена.")

        elif operation == "update_caretaker":
            server.update_caretaker()

        elif operation == "update_caretaker_legacy":
            # Обновление управляющего скрипта в первых его версиях, когда ещё не была реализована тихая установка.
            server.update_caretaker_legacy()

    except Exception as e:
        print("Для сервера {0}: {1}".format(server_id, str(e)))
        pprint(''.join(traceback.format_tb(e.__traceback__)))
        server.log(str(e))

    del server


@background
def package_task(package_id, operation, package_type):

    # Fix temporary (2006, 'MySQL server has gone away')
    from django.db import close_old_connections
    close_old_connections()

    try:
        if operation == "install_package":

            if package_type == "master":
                servers = Server.objects.filter(parent=None)
            else:
                servers = Server.objects.exclude(parent=None)

            for server in servers:
                with suppress(Exception):
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
