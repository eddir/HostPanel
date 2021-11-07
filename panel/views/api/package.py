from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from panel.models import SRPackage, MPackage, CPackage
from panel.serializers import SRPackageSerializer, MPackageSerializer, CPackageSerializer
from panel.tasks import tasks
from panel.utils import api_response


class PackageInstanceView(APIView):

    @staticmethod
    def post(request, pk, package_type):
        """Установка сборки во все сервера"""
        tasks.package_task(pk, "install_package", package_type)
        return api_response("Сборка установлена")

    @staticmethod
    def delete(request, pk, package_type):
        """Удаление сборки через api"""
        if package_type == "master":
            MPackage.objects.get(id=pk).delete()
        elif package_type == "spawner":
            SRPackage.objects.get(id=pk).delete()
        elif package_type == "custom":
            CPackage.objects.get(id=pk).delete()
        else:
            raise ValueError("Неизвестный тип сборки " + package_type)

        return api_response("Сборка удалена")


class PackageView(APIView):
    parser_classes = (MultiPartParser,)

    @staticmethod
    def get(request, package_type):
        """Получение всех сборок"""
        if package_type == "master":
            serializer = MPackageSerializer(MPackage.objects.all(), many=True)
        elif package_type == "spawner":
            serializer = SRPackageSerializer(SRPackage.objects.all(), many=True)
        elif package_type == "custom":
            serializer = CPackageSerializer(CPackage.objects.all(), many=True)
        else:
            raise ValueError("Неизвестный тип сборки " + package_type)

        return api_response(serializer.data)

    @staticmethod
    def post(request, package_type):
        """Загрузка сборки"""
        if package_type == "master":
            serializer = MPackageSerializer(data=request.data)
        elif package_type == "spawner":
            serializer = SRPackageSerializer(data=request.data)
        elif package_type == "custom":
            serializer = CPackageSerializer(data=request.data)
        else:
            raise ValueError("Неизвестный тип сборки " + package_type)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return api_response("Сборка загружена")
