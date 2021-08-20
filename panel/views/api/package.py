from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from panel.models import SRPackage, MPackage
from panel.serializers import SRPackageSerializer, MPackageSerializer
from panel.tasks import tasks
from panel.utils import api_response


class MPackageView(APIView):
    parser_classes = (MultiPartParser,)

    @staticmethod
    def get(request):
        """Получение всех сборок Master"""
        packages = MPackage.objects.all()
        serializer = MPackageSerializer(packages, many=True)
        return api_response(serializer.data)

    @staticmethod
    def post(request):
        """Загрузка сборки Master"""
        serializer = MPackageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return api_response("Сборка загружена")


class MPackageInstanceView(APIView):

    @staticmethod
    def get(request, pk):
        """Получение информации о сборке"""
        return api_response(MPackage.objects.filter(id=pk).values()[0])

    @staticmethod
    def post(request, pk):
        """Установка сборки во все сервера"""
        tasks.package_task(pk, "install_package", "master")
        return api_response("Сборка установлена")

    @staticmethod
    def delete(request, pk):
        """Удаление сборки через api"""
        MPackage.objects.get(id=pk).delete()
        return api_response("Сборка удалена")


class SRPackageInstanceView(APIView):

    @staticmethod
    def post(request, pk):
        """Установка сборки во все сервера"""
        tasks.package_task(pk, "install_package", "spawner")
        return api_response("Сборка установлена")

    @staticmethod
    def delete(request, pk):
        """Удаление сборки через api"""
        SRPackage.objects.get(id=pk).delete()
        return api_response("Сборка удалена")


class SRPackageView(APIView):
    parser_classes = (MultiPartParser,)

    @staticmethod
    def get(request):
        """Получение всех сборок Spawner"""
        packages = SRPackage.objects.all()
        serializer = SRPackageSerializer(packages, many=True)
        return api_response(serializer.data)

    @staticmethod
    def post(request):
        """Загрузка новой сборки Spawner"""
        serializer = SRPackageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return api_response("Сборка загружена")
