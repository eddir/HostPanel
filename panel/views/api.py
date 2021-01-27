import json
import os
from pprint import pprint

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from HostPanel.settings import MEDIA_ROOT
from panel import tasks
from panel.models import ServerStatus, Server, MPackage, SRPackage
from panel.serializers import MPackageSerializer, ServerStatusSerializer, ServerSerializer, MPackageSerializer, \
    SRPackageSerializer
from panel.tasks import init_server


class ServerView(APIView):
    # Инициализация и получение списка всех серверов

    def get(self, request):
        servers = ServerSerializer(Server.objects.all(), many=True)
        m_packages = MPackageSerializer(MPackage.objects.all(), many=True)
        sr_packages = SRPackageSerializer(SRPackage.objects.all(), many=True)
        return Response({
            "servers": servers.data,
            "m_packages": m_packages.data,
            "sr_packages": sr_packages.data,
        })

    def post(self, request):
        server = request.data
        serializer = ServerSerializer(data=server)
        server_saved = None

        if serializer.is_valid(raise_exception=True):
            server_saved = serializer.save()
            init_server(server_saved.id)

        return Response({"success": "Сервер '{}' добавлен.".format(server_saved.name)})


@method_decorator(csrf_exempt, name='dispatch')
class ServerInstanceView(APIView):
    # Запуск, остановка и получение данных о сервере

    def get(self, request, pk):
        try:
            return Response({"server": Server.objects.filter(id=pk).values(
                'id', 'ip', 'log', 'name', 'password_root', 'password_single', 'ssh_key', 'user_root',
                'user_single', 'm_package__name', 'sr_package__name', 'm_package__created_at',
                'sr_package__created_at', 'config')[0],
                             "status": ServerStatus.objects.filter(server=pk).values().last() or None})
        except IndexError:
            return Response({"server": None, "status": None})

    def put(self, request, pk):
        tasks.start_server(pk)
        return Response({"success": "Сервер запущен."})

    def delete(self, request, pk):
        tasks.stop_server(pk)
        return Response({"success": "Сервер остановлен."})


@method_decorator(csrf_exempt, name='dispatch')
class ServerStatusView(APIView):
    # Состояния сервера в моменте времени и информация о нагрузке

    def get(self, request):
        stats = ServerStatus.objects.all()
        serializer = ServerSerializer(stats, many=True)
        return Response({"stats": serializer.data})

    def post(self, request):
        stats = request.data
        serializer = ServerStatusSerializer(data=stats)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Статус сервера обновлён."})


@method_decorator(csrf_exempt, name='dispatch')
class ServerOnlineView(APIView):
    # Тестовый view для проверки связи с серевером

    def get(self, request, pk):
        return Response({"online": tasks.get_online(Server.objects.get(pk=pk))})


class MPackageView(APIView):
    # Загрузка сборки master
    parser_classes = (MultiPartParser,)

    def get(self, request):
        packages = MPackage.objects.all()
        serializer = MPackageSerializer(packages, many=True)
        return Response({"packages": serializer.data})

    def post(self, request):
        serializer = MPackageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Сборка загружена"})


@method_decorator(csrf_exempt, name='dispatch')
class MPackageInstanceView(APIView):
    # Получение информации о сборке

    def get(self, request, pk):
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


class SRPackageView(APIView):
    # Загрузка сборки spawner + room
    parser_classes = (MultiPartParser,)

    def get(self, request):
        packages = SRPackage.objects.all()
        serializer = SRPackageSerializer(packages, many=True)
        return Response({"packages": serializer.data})

    def post(self, request):
        serializer = SRPackageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Сборка загружена"})


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def update_config(request, pk):
    server = Server.objects.filter(id=pk)
    if server:
        server[0].config = json.loads(request.body.decode('utf-8'))['config']
        server[0].save()
        tasks.update_config(pk)
        return Response({"success": "Конфиг обновлён"})
    else:
        return Response({"error": "Сервер не найден"})
