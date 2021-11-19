import datetime
from pprint import pprint

from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.timezone import now
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from panel.models import Status, Dedic, SRPackage, MPackage, Server, Online, CPackage
from panel.serializers import ServerSerializer, DedicSerializer, SRPackageSerializer, MPackageSerializer, \
    StatusSerializer, CPackageSerializer
from panel.tasks import tasks
from panel.utils import api_response


class ServerView(APIView):

    @staticmethod
    def get(request):
        """Универсальный запрос. Возвращает список всех серверов, сборок и дедиков"""

        servers = ServerSerializer(Server.objects.all(), many=True)
        m_packages = MPackageSerializer(MPackage.objects.all(), many=True)
        sr_packages = SRPackageSerializer(SRPackage.objects.all(), many=True)
        c_packages = CPackageSerializer(CPackage.objects.all(), many=True)
        dedics = DedicSerializer(Dedic.objects.all(), many=True)

        return api_response({
            "servers": servers.data,
            "m_packages": m_packages.data,
            "sr_packages": sr_packages.data,
            "c_packages": c_packages.data,
            "dedics": dedics.data
        })

    @staticmethod
    def post(request):
        """Инициализация сервера"""
        request.data['watchdog_port'] = 8000

        serializer = ServerSerializer(data=request.data)
        server_saved = None

        if serializer.is_valid(raise_exception=True):
            dedic = Dedic.objects.get(id=request.data['dedic'])

            if request.data['type'] not in ["master", "spawner", "custom"]:
                raise ValueError("Неизвестный тип сервера %s" % request.data['type'])

            if Server.objects.filter(dedic__ip=dedic.ip, dedic__user_single=dedic.user_single).exists():
                raise ValueError("Не стоит запускать 2 сервера на одном IP и юзвере")

            while Server.objects.filter(
                    dedic__ip=dedic.ip,
                    watchdog_port=serializer.validated_data['watchdog_port']
            ).exists():
                serializer.validated_data['watchdog_port'] += 1

            server_saved = serializer.save()
            tasks.server_task(server_saved.id, "init")
            Status(server=server_saved, condition=Status.Condition.INSTALLED).save()

        return api_response("Сервер '{}' добавлен.".format(server_saved.name))


class ServerInstanceView(APIView):

    @staticmethod
    def get(request, pk):
        """Информаиця о конкретном сервере"""
        server = Server.objects.filter(id=pk)
        server_obj = server.last()
        rooms = None

        server_data = server.values(
            'id', 'log', 'name', 'config', 'processes', 'watchdog_port',

            'dedic__password_root', 'dedic__password_single', 'dedic__user_root', 'dedic__user_single',
            'dedic__ssh_key', 'dedic__ip', 'dedic__name',

            'package__mpackage__name', 'package__mpackage__created_at', 'package__mpackage__id',

            'package__srpackage__name', 'package__srpackage__created_at', 'package__srpackage__id',

            'package__cpackage__name', 'package__cpackage__created_at', 'package__cpackage__id'
        )[0]

        online = Online.objects.filter(
            server=pk,
            created_at__gte=(now() - datetime.timedelta(minutes=10))
        ).first()

        if online:
            server_data['online'] = online.online
        else:
            server_data['online'] = 0

        server_data['package'] = {
            'id': server_data['package__mpackage__id'] or server_data['package__srpackage__id'] or server_data[
                'package__cpackage__id'],  # todo: переделать
            'name': server_data['package__mpackage__name'] or server_data['package__srpackage__name'] or server_data[
                'package__cpackage__name'],
            'created_at': server_data['package__mpackage__created_at'] or server_data[
                'package__srpackage__created_at'] or server_data['package__cpackage__created_at'],
        }

        try:
            status = Status.objects.filter(server=server_obj).values().last()
        except IndexError:
            status = None

        server_data['is_online'] = False

        if status and status["condition"] == Status.Condition.RUNNING:

            # проверяем создан ли статус 10 минут назад
            if (timezone.now() - status["created_at"]) <= datetime.timedelta(minutes=10):
                server_data['is_online'] = True

            if server_obj.parent is None:
                rooms = list(Online.objects.filter(
                    server__in=list(Server.objects.filter(parent=pk).values_list('id', flat=True))
                ))

        return api_response({
            "children": Server.objects.filter(parent=pk).exists(),
            "server": server_data,
            "status": status,
            "rooms": rooms,
            "history": {
                "status": StatusSerializer(
                    Status.objects.filter(
                        server=pk,
                        condition=Status.Condition.RUNNING,
                        created_at__gte=(now() - datetime.timedelta(days=1))
                    ), many=True).data,
                "online": list(
                    Online.objects.filter(server=pk, created_at__gte=(now() - datetime.timedelta(days=1))).values()),
            }
        })

    @staticmethod
    def post(request, pk):
        """
        Переустановка сервера

        :param pk:
        :param request:
        :return:
        """
        if 'package' in request.data:
            server = Server.objects.get(id=pk)
            server.package_id = request.data['package']
            server.save()
            tasks.server_task(pk, "update")
            return api_response("Сборка устанавливается")
        else:
            tasks.server_task(pk, "reinstall")
        return api_response("Сервер переустанавливается.")


class StartServer(APIView):

    @staticmethod
    def post(request, pk):
        """Запуск сервера"""
        tasks.server_task(pk, "start")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.STARTS).save()
        return api_response("Сервер запущен.")


class StopServer(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request, pk):
        """Остановка сервера"""
        tasks.server_task(pk, "stop")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.STOPPED).save()
        return api_response("Сервер остановлен.")


class DestroyServer(APIView):

    @staticmethod
    def post(request, pk):
        """Удалять вместе с файлами на сервере"""
        tasks.server_task(pk, "delete")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.PAUSED).save()
        return api_response("Сервер удалён.")


class ForgetServer(APIView):

    @staticmethod
    def post(request, pk):
        """Удаление данных о сервере из базы"""
        server = Server.objects.get(id=pk)
        server.delete()
        return api_response("Сервер убран")


class RebootServer(APIView):

    @staticmethod
    def post(request, pk):
        """Ребут вдс"""
        tasks.server_task(pk, "reboot")
        return api_response("Ребут начат")


class UpdateConfig(APIView):

    @staticmethod
    def post(request, pk):
        """Внесение изменений в конфиг сервера"""
        server = get_object_or_404(Server, pk=pk)
        server.config = request.data['config']
        server.save()
        tasks.server_task(pk, "update_config")

        return api_response("Конфиг обновлён")


class UpdateCaretaker(APIView):

    @staticmethod
    def post(request, pk):
        """Обновление скрипта Watchdog"""
        tasks.server_task(pk, 'update_caretaker')
        return api_response("Обновление запущено")


class SetStatus(APIView):

    @staticmethod
    def post(request, pk):
        Status(server=Server.objects.get(id=pk), condition=request.data['condition']).save()
        return api_response("Статус установлен")
