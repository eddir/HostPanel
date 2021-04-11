import datetime
import sys

from packaging import version
from django.template.defaultfilters import filesizeformat
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from background_task.models import Task

from HostPanel.settings import MEDIA_ROOT
from panel.tasks import tasks
from panel.models import Status, Server, MPackage, SRPackage, Online, Dedic
from panel.serializers import StatusSerializer, ServerSerializer, MPackageSerializer, SRPackageSerializer, \
    OnlineSerializer, DedicSerializer, TaskSerializer
from panel.utils import get_caretaker_version


class DedicView(APIView):
    # Инициализация и получение списка всех дедиков

    @staticmethod
    def get(request):
        """Возвращает список существуюзих дедиков"""
        dedics = DedicSerializer(Dedic.objects.all(), many=True)

        return Response({
            'dedics': dedics.data
        })

    @staticmethod
    def post(request):
        """Добавляет дедик по заданным параметрам и добавляет задание на подключение"""
        serializer = DedicSerializer(data=request.data)
        dedic_saved = None

        if serializer.is_valid(raise_exception=True):
            dedic_saved = serializer.save()
            tasks.dedic_task(dedic_saved.id, "init")

        return Response({
            "ok": True,
            "dedic_id": dedic_saved.id,
            "success": "Вдс '{}' добавлен.".format(dedic_saved.name)
        })


class ServerView(APIView):
    # Инициализация и получение списка всех серверов

    @staticmethod
    def get(request):
        servers = ServerSerializer(Server.objects.all(), many=True)
        m_packages = MPackageSerializer(MPackage.objects.all(), many=True)
        sr_packages = SRPackageSerializer(SRPackage.objects.all(), many=True)
        dedics = DedicSerializer(Dedic.objects.all(), many=True)

        return Response({
            "servers": servers.data,
            "m_packages": m_packages.data,
            "sr_packages": sr_packages.data,
            "dedics": dedics.data
        })

    @staticmethod
    def post(request):
        """
        Инициализация сервера

        :param request:
        :return:
        """
        serializer = ServerSerializer(data=request.data)
        server_saved = None

        if serializer.is_valid(raise_exception=True):
            dedic = Dedic.objects.get(id=request.data['dedic'])
            # TODO: проверочка в соотвествии с изменениями в дедиках
            if request.data['parent'] is None and Server.objects.filter(dedic__ip=dedic.ip, parent=None).exists():
                raise ValueError("Нельзя запускать 2 мастера на 1 ip")
            elif Server.objects.filter(dedic__ip=dedic.ip).exclude(parent=None).exists():
                raise ValueError("Нельзя запускать 2 спавнера на 1 ip")

            if Server.objects.filter(dedic__ip=dedic.ip, dedic__user_single=dedic.user_single).exists():
                raise ValueError("Не стоит запускать 2 сервера на одном IP и юзвере")

            server_saved = serializer.save()
            tasks.server_task(server_saved.id, "init")
            Status(server=server_saved, condition=Status.Condition.INSTALLED).save()

        return Response({
            "ok": True,
            "server_id": server_saved.id,
            "success": "Сервер '{}' добавлен.".format(server_saved.name)
        })


@method_decorator(csrf_exempt, name='dispatch')
class ServerInstanceView(APIView):
    # Запуск, остановка, старт ребут и получение данных о сервере

    @staticmethod
    def get(request, pk):
        try:
            server = Server.objects.filter(id=pk)
            server_obj = server.last()
            rooms = None

            try:
                status = Status.objects.filter(server=server_obj).values().last()
            except IndexError:
                status = None

            if status and status["condition"] is Status.Condition.RUNNING:
                if server_obj.parent is None:
                    rooms = Online.objects.filter(
                        server__in=list(Server.objects.filter(parent=pk).values_list('id', flat=True))
                    ).values()

                for key in ["hdd_available", "hdd_usage", "ram_available", "ram_usage"]:
                    status[key] = filesizeformat(status[key])

            server_data = server.values(
                'id', 'dedic__ip', 'log', 'name', 'dedic__password_root', 'dedic__password_single', 'dedic__ssh_key',
                'dedic__user_root', 'dedic__user_single', 'package__mpackage__name', 'package__srpackage__name',
                'package__mpackage__created_at', 'package__srpackage__created_at', 'config')[0]

            online = Online.objects.filter(
                server=pk,
                created_at__gte=(now() - datetime.timedelta(minutes=10))
            ).first()

            if online:
                server_data['online'] = online.online
            else:
                server_data['online'] = 0

            server_data['package'] = {
                'name': server_data['package__mpackage__name'] or server_data['package__srpackage__name'],
                'created_at': server_data['package__mpackage__created_at'] or server_data[
                    'package__srpackage__created_at'],
            }

            return Response({
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
                    "online": Online.objects.filter(server=pk, created_at__gte=(now() - datetime.timedelta(days=1))).values(),
                }
            })
        except IndexError:
            return Response({"server": None, "status": None})

    @staticmethod
    def put(request, pk):
        tasks.server_task(pk, "start")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.STARTS).save()
        return Response({"success": "Сервер запущен."})

    @staticmethod
    def patch(request, pk):
        tasks.server_task(pk, "reboot")
        return Response({"Success": "Ребут начат"})

    @staticmethod
    def delete(request, pk):
        tasks.server_task(pk, "stop")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.PAUSED).save()
        return Response({"success": "Сервер остановлен."})

    @staticmethod
    def post(request, pk):
        """
        Переустановка сервера

        :param pk:
        :param request:
        :return:
        """
        tasks.server_task(pk, "reinstall")
        return Response({"success": "Сервер переустанавливается."})


@method_decorator(csrf_exempt, name='dispatch')
class StatusView(APIView):
    # Состояния сервера в моменте времени и информация о нагрузке

    @staticmethod
    def get(request):
        stats = Status.objects.all()
        serializer = ServerSerializer(stats, many=True)
        return Response({"stats": serializer.data})

    @staticmethod
    def post(request):
        stat = {
            'server': request.data['server'],
            'cpu_usage': request.data['cpu_usage'],
            'ram_usage': request.data['ram_usage'],
            'ram_available': request.data['ram_available'],
            'hdd_usage': request.data['hdd_usage'],
            'hdd_available': request.data['hdd_available']
        }
        serializer = StatusSerializer(data=stat)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        if 'caretaker_version' in request.data:
            client_version = version.parse(request.data['caretaker_version'])
        else:
            client_version = version.parse("1.0.0")

        if client_version < version.parse("2.0.0"):
            tasks.server_task(request.data['server'], 'update_caretaker_legacy')

        elif client_version < version.parse(get_caretaker_version()):
            tasks.server_task(request.data['server'], 'update_caretaker')

        return Response({"success": "Статус сервера обновлён."})


@method_decorator(csrf_exempt, name='dispatch')
class OnlineView(APIView):

    @staticmethod
    def post(request):
        serializer = OnlineSerializer(data={
            'server': request.data['server'],
            'online': request.data['online']['AllPlayers']
        })
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        for ip, spawner in request.data['online']['OnlineInRooms'].items():
            server = Server.objects.filter(parent=request.data['server'], ip=ip).first()
            for room in spawner:
                serializer = OnlineSerializer(data={
                    'server': server.id,
                    'port': room['port'],
                    'online': room['onlineCount'],
                    'max_online': room['maxOnline']
                })
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

        return Response({"success": "Онлайн сервера обновлён."})


class MPackageView(APIView):
    # Загрузка сборки master
    parser_classes = (MultiPartParser,)

    @staticmethod
    def get(request):
        packages = MPackage.objects.all()
        serializer = MPackageSerializer(packages, many=True)
        return Response({"packages": serializer.data})

    @staticmethod
    def post(request):
        serializer = MPackageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Сборка загружена"})


@method_decorator(csrf_exempt, name='dispatch')
class MPackageInstanceView(APIView):
    # Получение информации о сборке

    @staticmethod
    def get(request, pk):
        try:
            return Response({
                "code": True,
                "data": {
                    "package": MPackage.objects.filter(id=pk).values()[0]
                }
            })
        except IndexError:
            return Response({
                "ok": False,
                "error": {
                    "id": 404,
                    "message": "Undefined value"
                }
            })

    # Установка сборки во все сервера

    @staticmethod
    def post(request, pk):
        tasks.package_task(pk, "install_package", "master")
        return Response({"success": "Сборка установлена"})


@method_decorator(csrf_exempt, name='dispatch')
class SRPackageInstanceView(APIView):
    # Установка сборки во все сервера

    @staticmethod
    def post(request, pk):
        tasks.package_task(pk, "install_package", "spawner")
        return Response({"success": "Сборка установлена"})


class SRPackageView(APIView):
    # Загрузка сборки spawner + room
    parser_classes = (MultiPartParser,)

    @staticmethod
    def get(request):
        packages = SRPackage.objects.all()
        serializer = SRPackageSerializer(packages, many=True)
        return Response({"packages": serializer.data})

    @staticmethod
    def post(request):
        serializer = SRPackageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Сборка загружена"})


class TaskPackageView(APIView):
    # Получение списка текущих фоновых задач

    @staticmethod
    def get(request):
        tasks_list = Task.objects.all()
        serializer = TaskSerializer(tasks_list, many=True)
        return Response({"tasks": serializer.data})


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def update_config(request, pk):
    server = Server.objects.filter(id=pk)
    if server:
        server[0].config = request.data['config']
        server[0].save()
        tasks.server_task(pk, "update_config")
        return Response({"success": "Конфиг обновлён"})
    else:
        return Response({"error": "Сервер не найден"})
