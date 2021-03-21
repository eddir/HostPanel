import json
from pprint import pprint
from unittest import TestCase

from background_task.models import Task
from django.test import Client
from django.utils.timezone import now


class TasksTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        Task.objects.all().delete()

    def assertTaskExists(self, name, params):
        self.assertTrue(Task.objects.filter(task_name=name, task_params=json.dumps([params, {}])).exists())

    def test_api_server_create(self):

        # Тест создания дедика

        response = self.client.post('/api/dedics/', {
            'name': 'Unit test dedic #1',
            'ip': '127.0.0.1',
            'user_root': 'root',
            'password_root': 'testing123',
            'user_single': 'UnitTest',
            'ssh_key': False
        })
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode('utf-8'))
        self.assertTrue(content['ok'])
        dedic_id = content['dedic_id']

        self.assertTaskExists('panel.tasks.tasks.dedic_task', [dedic_id, "init"])

        # Тест попытки переподключиться

        response = self.client.get('/dedic/' + str(dedic_id) + '/reconnect/')
        self.assertEqual(response.status_code, 302)

        self.assertTaskExists('panel.tasks.tasks.dedic_task', [dedic_id, "reconnect"])

        # Тест создания сервера

        response = self.client.post('/api/servers/', {
            'parent': "",
            'dedic': dedic_id,
            'name': 'Unit test server #1',
            'config': "",
            'package': 3
        })
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode('utf-8'))
        self.assertTrue(content['ok'])
        server_id = content['server_id']

        self.assertTaskExists('panel.tasks.tasks.server_task', [server_id, "init"])

        # Тест создания сервера на том же дедике

        response = self.client.post('/api/servers/', {
            'parent': "",
            'dedic': dedic_id,
            'name': 'Unit test server #2',
            'config': "",
            'package': 3
        })
        self.assertEqual(response.status_code, 500)

        # Удаление
        response = self.client.delete('/server/' + str(server_id) + '/delete/confirm/')
        self.assertEqual(response.status_code, 200)
