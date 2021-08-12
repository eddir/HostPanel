from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from panel.models import SRPackage, MPackage
from panel.serializers import SRPackageSerializer, MPackageSerializer
from panel.tasks import tasks


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


class MPackageInstanceView(APIView):

    @staticmethod
    def get(request, pk):
        # Получение информации о сборке
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

    @staticmethod
    def post(request, pk):
        # Установка сборки во все сервера
        tasks.package_task(pk, "install_package", "master")
        return Response({"success": "Сборка установлена"})

    # Удаление сборки через api
    @staticmethod
    def delete(request, pk):
        MPackage.objects.get(id=pk).delete()
        return Response({"success": "Сборка удалена"})


class SRPackageInstanceView(APIView):

    @staticmethod
    def post(request, pk):
        # Установка сборки во все сервера
        tasks.package_task(pk, "install_package", "spawner")
        return Response({"success": "Сборка установлена"})

    @staticmethod
    def delete(request, pk):
        # Удаление сборки через api
        SRPackage.objects.get(id=pk).delete()
        return Response({"success": "Сборка удалена"})


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
