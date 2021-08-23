import datetime

from django.template.defaultfilters import filesizeformat
from django.utils.timezone import now
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from panel.models import Status, Dedic, SRPackage, MPackage, Server, Online
from panel.serializers import ServerSerializer, DedicSerializer, SRPackageSerializer, MPackageSerializer, \
    StatusSerializer
from panel.tasks import tasks
from panel.utils import api_response


class ServerView(APIView):

    @staticmethod
    def get(request):
        """Универсальный запрос. Возвращает список всех серверов, сборок и дедиков"""

        servers = ServerSerializer(Server.objects.all(), many=True)
        m_packages = MPackageSerializer(MPackage.objects.all(), many=True)
        sr_packages = SRPackageSerializer(SRPackage.objects.all(), many=True)
        dedics = DedicSerializer(Dedic.objects.all(), many=True)

        return api_response({
            "servers": servers.data,
            "m_packages": m_packages.data,
            "sr_packages": sr_packages.data,
            "dedics": dedics.data
        })

    @staticmethod
    def post(request):
        """Инициализация сервера"""
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

        return api_response("Сервер '{}' добавлен.".format(server_saved.name))


class ServerInstanceView(APIView):

    @staticmethod
    def get(request, pk):
        """Информаиця о конкретном сервере"""
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
                'package__mpackage__created_at', 'package__srpackage__created_at',
                'package__mpackage__id', 'package__srpackage__id', 'config', 'bin_path')[0]

            online = Online.objects.filter(
                server=pk,
                created_at__gte=(now() - datetime.timedelta(minutes=10))
            ).first()

            if online:
                server_data['online'] = online.online
            else:
                server_data['online'] = 0

            server_data['package'] = {
                'id': server_data['package__mpackage__id'] or server_data['package__srpackage__id'],  # todo: переделать
                'name': server_data['package__mpackage__name'] or server_data['package__srpackage__name'],
                'created_at': server_data['package__mpackage__created_at'] or server_data[
                    'package__srpackage__created_at'],
            }

            return api_response({
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
                    "online": list(Online.objects.filter(server=pk,
                                                         created_at__gte=(
                                                                 now() - datetime.timedelta(days=1))).values()),
                }
            })
        except IndexError:
            return api_response({"server": None, "status": None})

    @staticmethod
    def post(request, pk):
        """
        Переустановка сервера

        :param pk:
        :param request:
        :return:
        """
        if 'package' in request.data:
            server = Server.objects.get(id=pk)
            server.package_id = request.data['package']
            server.save()
            tasks.server_task(pk, "update")
            return api_response("Сборка устанавливается")
        else:
            tasks.server_task(pk, "reinstall")
            return api_response("Сервер переустанавливается.")


class StartServer(APIView):

    @staticmethod
    def post(request, pk):
        """Запуск сервера"""
        tasks.server_task(pk, "start")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.STARTS).save()
        return api_response("Сервер запущен.")


class StopServer(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request, pk):
        """Остановка сервера"""
        tasks.server_task(pk, "stop")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.STOPPED).save()
        return api_response("Сервер остановлен.")


class DestroyServer(APIView):

    @staticmethod
    def post(request, pk):
        """Удалять вместе с файлами на сервере"""
        tasks.server_task(pk, "delete")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.PAUSED).save()
        return api_response("Сервер удалён.")


class ForgetServer(APIView):

    @staticmethod
    def post(request, pk):
        """Удаление данных о сервере из базы"""
        server = Server.objects.get(id=pk)
        server.delete()
        return api_response("Сервер убран")


class RebootServer(APIView):

    @staticmethod
    def post(request, pk):
        """Ребут вдс"""
        tasks.server_task(pk, "reboot")
        return api_response("Ребут начат")


class UpdateConfig(APIView):

    @staticmethod
    def post(request, pk):
        """Внесение изменений в конфиг сервера"""
        server = get_object_or_404(Server, pk=pk)
        server.config = request.data['config']
        server.save()
        tasks.server_task(pk, "update_config")

        return api_response("Конфиг обновлён")


class UpdateCaretaker(APIView):

    @staticmethod
    def post(request, pk):
        """Обновление скрипта Caretaker"""
        tasks.server_task(pk, 'update_caretaker')
        return api_response("Обновление запущено")


class SetStatus(APIView):

    @staticmethod
    def post(request, pk):
        Status(server=Server.objects.get(id=pk), condition=request.data['condition']).save()
        return api_response("Статус установлен")


class SetBinPath(APIView):

    @staticmethod
    def post(request, pk):
        server = get_object_or_404(Server, pk=pk)
        server.bin_path = request.data['bin_path']
        server.save()
        return api_response("Путь установлен")
