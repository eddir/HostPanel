from django.test import TestCase

from panel.models import MPackage, Dedic, Server, Status, SRPackage
from panel.tasks.DedicUnit import DedicUnit
from panel.tasks.ServerUnit import ServerUnit


class TasksTestCase(TestCase):

    def test_servers_create(self):
        m_package = MPackage.objects.create(
            name="MPackage test",
            master="packages/Master.zip"
        )
        m_package.save()

        sr_package = SRPackage.objects.create(
            name="SRPackage test",
            spawner="packages/Spawner.zip",
            room="packages/Room.zip"
        )

        # Создание дедика
        # noinspection SpellCheckingInspection
        dedic = Dedic.objects.create(
            name="Dedic Master test",
            ip="5.180.138.187",
            user_root="root",
            user_single="unittest",
            password_root="CHBE644Q7x82",
            ssh_key=False
        )
        dedic.save()

        d = DedicUnit(dedic)
        d.init()

        dedic.refresh_from_db()
        self.assertEqual(dedic.condition, True)

        cmd = d.command('echo ok', root=True, output=True)
        self.assertEqual(cmd[0], 'ok\n')

        last_listen = dedic.last_listen
        d.reconnect()
        dedic.refresh_from_db()
        self.assertNotEqual(last_listen, dedic.last_listen)

        # Создание мастера
        master = Server.objects.create(
            dedic=dedic,
            name="Master test",
            package=m_package
        )
        master.save()

        s = self._test_server(master)

        s.update_caretaker()
        master.refresh_from_db()
        self.assertTrue("Обновление Caretaker завершено" in master.log)
        self.assertEqual(master.get_last_status().condition, Status.Condition.STOPPED)

        # Создание спавнера
        spawner = Server.objects.create(
            parent=master,
            dedic=dedic,
            name="Spawner test",
            package=sr_package
        )
        spawner.save()

        self._test_server(spawner)

        # Сборка мусора
        s.delete()
        d.delete()

        print("[*] Тест фоновых задач пройден!")

    def _test_server(self, server):
        s = ServerUnit(server)
        s.init()

        self.assertEqual(server.get_last_status(), None)

        s.stop()
        server.refresh_from_db()
        self.assertEqual(server.get_last_status().condition, Status.Condition.STOPPED)

        return s
