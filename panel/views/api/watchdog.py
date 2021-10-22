from pprint import pprint

import requests
from django.http import HttpResponse, FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from panel.models import Server
from panel.utils import api_response


@method_decorator(csrf_exempt, name='dispatch')
class LogsView(APIView):

    @staticmethod
    def get(request, pk):
        """Получение состояния сервера"""
        server = Server.objects.get(pk=pk)
        data = requests.get("http://" + server.dedic.ip + ":" + str(server.watchdog_port) + "/logs/")
        return api_response(data.json())


@method_decorator(csrf_exempt, name='dispatch')
class LogsDownloadView(APIView):

    @staticmethod
    def get(request, pk, file):
        size = request.query_params.get('size')
        number = request.query_params.get('number')

        response = HttpResponse(
            requests.get('http://51.195.97.80:8001/logs/download/' + file + '/?size=' + size + '&number=' + number),
            content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = ('attachment; filename={0}'.format(file))

        return response


@method_decorator(csrf_exempt, name='dispatch')
class LogsRemoveView(APIView):

    @staticmethod
    def post(request, pk, file):
        server = Server.objects.get(pk=pk)
        data = requests.post("http://" + server.dedic.ip + ":" + str(server.watchdog_port) + "/logs/remove/" + file)
        pprint(data.text)
        return api_response("Файл удалён")

