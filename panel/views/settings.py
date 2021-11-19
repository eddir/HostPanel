from rest_framework.views import APIView

from HostPanel import settings
from panel.models import Subscriber
from panel.serializers import SubscriberSerializer
from panel.utils import api_response


class TelegramSubscriptionsView(APIView):

    @staticmethod
    def get(request):
        """Список всех подписчиков"""
        return api_response(SubscriberSerializer(Subscriber.objects.all(), many=True).data)

    @staticmethod
    def post(request):
        """Оформить подписку"""
        serializer = SubscriberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return api_response("Подписка оформлена")


class TelegramSubscriberView(APIView):

    @staticmethod
    def delete(request, pk):
        """Отменить подписку"""
        Subscriber.objects.get(id=pk).delete()
        return api_response("Подписка отменена")


class VersionView(APIView):

    @staticmethod
    def get(request):
        """Версия панели, Watchdog и базы данных MySQL"""
        return api_response({
            "panel": settings.PANEL_VERSION,
            "caretaker": settings.CARETAKER_VERSION,
            "mysql": settings.MYSQL_VERSION
        })


class PingView(APIView):

    @staticmethod
    def get(request):
        return api_response("Pong")
