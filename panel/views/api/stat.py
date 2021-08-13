from background_task.models import Task
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from packaging import version
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from HostPanel import settings
from panel.models import Status, Server, Dedic
from panel.serializers import TaskSerializer, OnlineSerializer, StatusSerializer, ServerSerializer
from panel.tasks import tasks
from panel.utils import get_caretaker_version


@method_decorator(csrf_exempt, name='dispatch')
class StatusView(APIView):
    # Состояния сервера в моменте времени и информация о нагрузке

    permission_classes = (AllowAny,)

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

        server = Server.objects.get(id=request.data['server'])
        server.dedic.last_listen = timezone.now()
        server.dedic.connection = True
        server.dedic.save()

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
    # Информация об онлайне на серверах

    permission_classes = (AllowAny,)

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


class TaskView(APIView):
    # Получение списка текущих фоновых задач

    @staticmethod
    def get(request):
        tasks_list = Task.objects.all()
        serializer = TaskSerializer(tasks_list, many=True)
        return Response({"tasks": serializer.data})

    @staticmethod
    def delete(request):
        Task.objects.all().delete()
        return Response({
            "ok": True,
            "success": "Задачи отменены"
        })


class VersionView(APIView):

    @staticmethod
    def get(request):
        return Response({
            "ok": True,
            "response": {
                "panel": settings.PANEL_VERSION,
                "caretaker": settings.CARETAKER_VERSION,
                "mysql": settings.MYSQL_VERSION
            }
        })
