import datetime

from django.template.defaultfilters import filesizeformat
from django.utils.timezone import now
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from panel.models import Status, Dedic, SRPackage, MPackage, Server, Online
from panel.serializers import ServerSerializer, DedicSerializer, SRPackageSerializer, MPackageSerializer, \
    StatusSerializer
from panel.tasks import tasks


class ServerView(APIView):

    @staticmethod
    def get(request):
        """Универсальный запрос. Возвращает список всех серверов, сборок и дедиков"""

        servers = ServerSerializer(Server.objects.all(), many=True)
        m_packages = MPackageSerializer(MPackage.objects.all(), many=True)
        sr_packages = SRPackageSerializer(SRPackage.objects.all(), many=True)
        dedics = DedicSerializer(Dedic.objects.all(), many=True)

        return Response({
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

        return Response({
            "ok": True,
            "server_id": server_saved.id,
            "success": "Сервер '{}' добавлен.".format(server_saved.name)
        })


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
                'package__mpackage__id', 'package__srpackage__id', 'config')[0]

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

            return Response({
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
                    "online": Online.objects.filter(server=pk,
                                                    created_at__gte=(now() - datetime.timedelta(days=1))).values(),
                }
            })
        except IndexError:
            return Response({"server": None, "status": None})

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
            return Response({"success": "Сборка устанавливается"})
        else:
            tasks.server_task(pk, "reinstall")
            return Response({"success": "Сервер переустанавливается."})


class StartServer(APIView):

    @staticmethod
    def post(request, pk):
        tasks.server_task(pk, "start")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.STARTS).save()
        return Response({"success": "Сервер запущен."})


class StopServer(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request, pk):
        tasks.server_task(pk, "stop")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.STOPPED).save()
        return Response({"success": "Сервер остановлен."})


class DestroyServer(APIView):

    @staticmethod
    def post(request, pk):
        # Удалять вместе с файлами на сервере
        tasks.server_task(pk, "delete")
        Status(server=Server.objects.get(id=pk), condition=Status.Condition.PAUSED).save()
        return Response({"success": "Сервер удалён."})


class ForgetServer(APIView):

    @staticmethod
    def post(request, pk):
        server = Server.objects.get(id=pk)
        server.delete()
        return Response({"success": "Сервер убран"})


class RebootServer(APIView):

    @staticmethod
    def post(request, pk):
        tasks.server_task(pk, "reboot")
        return Response({"success": "Ребут начат"})


class UpdateConfig(APIView):

    @staticmethod
    def post(request, pk):
        server = Server.objects.filter(id=pk)
        if server:
            server[0].config = request.data['config']
            server[0].save()
            tasks.server_task(pk, "update_config")
            return Response({"success": "Конфиг обновлён"})
        else:
            return Response({"error": "Сервер не найден"})


class UpdateCaretaker(APIView):

    @staticmethod
    def post(request, pk):
        tasks.server_task(pk, 'update_caretaker')
        return Response({"success": "Обновление запущено"})


class SetStatus(APIView):

    @staticmethod
    def post(request, pk):
        Status(server=Server.objects.get(id=pk), condition=request.data['condition']).save()
        return Response({"success": "Статус установлен"})
