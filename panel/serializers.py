import datetime
import json
import os

from background_task.models import Task
from django.template.defaultfilters import filesizeformat
from django.utils.timezone import now
from rest_framework import serializers

from panel.models import Server, Status, MPackage, SRPackage, Online, Dedic, CPackage


class DedicSerializer(serializers.ModelSerializer):
    has_child = serializers.SerializerMethodField()

    class Meta:
        model = Dedic
        fields = ('id', 'name', 'ip', 'user_root', 'password_root', 'user_single', 'password_single', 'ssh_key',
                  'condition', 'last_listen', 'log', 'has_child')

    @staticmethod
    def get_has_child(dedic):
        return Server.objects.filter(dedic=dedic).exists()

    def to_representation(self, instance):
        representation = super(DedicSerializer, self).to_representation(instance)
        return representation


class ServerSerializer(serializers.ModelSerializer):
    load = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    installed = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = ('id', 'parent', 'name', 'dedic', 'config', 'load', 'status', 'package', 'online', 'rooms',
                  'installed', 'custom', 'watchdog_port')

    @staticmethod
    def get_load(server):
        status = Status.objects.filter(server=server).last()
        return status is not None

    @staticmethod
    def get_status(server):
        status = Status.objects.filter(
            server=server, created_at__gte=(now() - datetime.timedelta(minutes=10))
        ).last()
        if status:
            return StatusSerializer(status).data
        else:
            return False

    @staticmethod
    def get_online(server):
        online = Online.objects.filter(
            server=server.id,
            created_at__gte=(now() - datetime.timedelta(minutes=10))
        ).first()
        if online:
            return online.online
        else:
            return 0

    @staticmethod
    def get_rooms(server):
        online = Online.objects.filter(
            server__in=list(Server.objects.filter(parent=server.id).values_list('id', flat=True)),
            created_at__gte=(now() - datetime.timedelta(minutes=10))
        )
        if online:
            return OnlineSerializer(online, many=True).data
        else:
            return False

    @staticmethod
    def get_installed(server):
        return Status.objects.filter(server=server).exists()


class MPackageSerializer(serializers.ModelSerializer):
    master_size = serializers.SerializerMethodField()

    class Meta:
        model = MPackage
        fields = ('id', 'name', 'created_at', 'master', 'master_size', 'bin_path')

    @staticmethod
    def get_master_size(package):
        return filesizeformat(os.path.getsize(package.master.path))

    def to_representation(self, instance):
        representation = super(MPackageSerializer, self).to_representation(instance)
        representation['created_at'] = instance.created_at.strftime("%d.%m.%Y %H:%M:%S")
        return representation


class SRPackageSerializer(serializers.ModelSerializer):
    spawner_size = serializers.SerializerMethodField()
    room_size = serializers.SerializerMethodField()

    class Meta:
        model = SRPackage
        fields = ('id', 'name', 'created_at', 'spawner', 'room', 'spawner_size', 'room_size', 'bin_path')

    @staticmethod
    def get_spawner_size(package):
        return filesizeformat(os.path.getsize(package.spawner.path))

    @staticmethod
    def get_room_size(package):
        return filesizeformat(os.path.getsize(package.room.path))

    def to_representation(self, instance):
        representation = super(SRPackageSerializer, self).to_representation(instance)
        representation['created_at'] = instance.created_at.strftime("%d.%m.%Y %H:%M:%S")
        return representation


class CPackageSerializer(serializers.ModelSerializer):
    archive_size = serializers.SerializerMethodField()

    class Meta:
        model = CPackage
        fields = ('id', 'name', 'created_at', 'archive', 'archive_size', 'bin_path')

    @staticmethod
    def get_archive_size(package):
        return filesizeformat(os.path.getsize(package.archive.path))

    def to_representation(self, instance):
        representation = super(CPackageSerializer, self).to_representation(instance)
        representation['created_at'] = instance.created_at.strftime("%d.%m.%Y %H:%M:%S")
        return representation


class StatusSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(queryset=Server.objects.all())
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True, default=None)

    class Meta:
        model = Status
        fields = '__all__'


class OnlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Online
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(TaskSerializer, self).to_representation(instance)

        params = json.loads(representation['task_params'])

        if representation['task_name'] == "panel.tasks.tasks.dedic_task":
            representation['unit_name'] = Dedic.objects.get(pk=params[0][0]).name
        elif representation['task_name'] == "panel.tasks.tasks.server_task":
            representation['unit_name'] = Server.objects.get(pk=params[0][0]).name
        elif representation['task_name'] == "panel.tasks.tasks.package_task":
            representation['unit_name'] = params[0][0]
        return representation
