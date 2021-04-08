import time
from pprint import pprint

from django.test import TestCase

from panel import tasks
from panel.models import MPackage, Dedic, Server, Status
from panel.tasks.DedicUnit import DedicUnit
from panel.tasks.ServerUnit import ServerUnit


class TasksTestCase(TestCase):

    def test_servers_create(self):
        mpackage = MPackage.objects.create(
            name="MPackage test",
            master="packages/Master.zip"
        )
        mpackage.save()

        dedic = Dedic.objects.create(
            name="Dedic Master test",
            ip="5.180.138.187",
            user_root="root",
            user_single="unittest1",
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

        master = Server.objects.create(
            dedic=dedic,
            name="Master test",
            package=mpackage
        )
        master.save()

        s = ServerUnit(master)
        s.init()

        self.assertEqual(master.get_last_status(), None)

        s.stop()
        master.refresh_from_db()
        self.assertEqual(master.get_last_status().condition, Status.Condition.STOPPED)

        s.update_caretaker()
        master.refresh_from_db()
        self.assertTrue("Обновление Caretaker завершено" in master.log)
        self.assertEqual(master.get_last_status().condition, Status.Condition.STOPPED)

        s.delete()
        d.delete()

