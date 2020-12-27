import os
from pprint import pprint

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from HostPanel.settings import MEDIA_ROOT
from panel import tasks
from panel.models import ServerStatus, Server, Package
from panel.serializers import PackageSerializer, ServerStatusSerializer, ServerSerializer
from panel.tasks import init_server


class ServerView(APIView):
    # Инициализация и получение списка всех серверов

    def get(self, request):
        servers = Server.objects.all()
        serializer = ServerSerializer(servers, many=True)
        return Response({"servers": serializer.data})

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
            return Response({"server": Server.objects.filter(id=pk).values()[0],
                             "status": ServerStatus.objects.filter(server=pk).values()[0] or None})
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


class PackageView(APIView):
    # Загрузка сборки
    parser_classes = (MultiPartParser,)

    def get(self, request):
        packages = Package.objects.all()
        serializer = PackageSerializer(packages, many=True)
        return Response({"packages": serializer.data})

    def post(self, request):
        """
        file_obj = request.FILES['file']
        destination = open('/Users/Username/' + file_obj.name, 'wb+')
        for chunk in file_obj.chunks():
            destination.write(chunk)
        destination.close()
        """

        data = request.data
        data["archive"] = request.FILES['file']

        serializer = PackageSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Сборка загружена"})


"""
    def post(self, request):
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Статус сервера обновлён."})
"""


@method_decorator(csrf_exempt, name='dispatch')
class PackageInstanceView(APIView):
    # Получение информации о сборке

    def get(self, request, pk):
        try:
            return Response({
                "code": True,
                "data": {
                    "package": Package.objects.filter(id=pk).values()[0]
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
