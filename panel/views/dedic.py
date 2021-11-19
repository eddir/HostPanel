from rest_framework.views import APIView

from panel.models import Dedic, Server
from panel.serializers import DedicSerializer
from panel.tasks import tasks
from panel.utils import api_response


class DedicView(APIView):

    @staticmethod
    def get(request):
        """Возвращает список существуюзих дедиков"""
        dedics = DedicSerializer(Dedic.objects.all(), many=True)
        return api_response(dedics.data)

    @staticmethod
    def post(request):
        """Добавляет дедик по заданным параметрам и добавляет задание на подключение"""
        serializer = DedicSerializer(data=request.data)
        dedic_saved = None

        if serializer.is_valid(raise_exception=True):
            dedic_saved = serializer.save()
            tasks.dedic_task(dedic_saved.id, "init")

        return api_response("Вдс '{}' добавлен.".format(dedic_saved.name))


class DedicInstanceView(APIView):

    @staticmethod
    def delete(request, pk):
        """Удаление дедика из панели вместе с пользователем из сервера"""
        if not Server.objects.filter(dedic=pk).exists():
            tasks.dedic_task(pk, "delete")
            return api_response("Удаление начато")
        else:
            raise ValueError("Невозможно удалить дедик с установленными на нём серверами.")


class ReconnectDedic(APIView):

    @staticmethod
    def post(request, pk):
        """Попытка переподключения"""
        tasks.dedic_task(pk, "reconnect")
        return api_response("Переподключение...")
