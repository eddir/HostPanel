import datetime
import os
from pprint import pprint

from django.template.defaultfilters import filesizeformat
from django.utils.timezone import now
from rest_framework import serializers

from panel.models import Server, Status, MPackage, SRPackage, Online


class ServerSerializer(serializers.ModelSerializer):
    load = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    installed = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = ('id', 'parent', 'name', 'ip', 'user_root', 'password_root', 'user_single', 'password_single',
                  'ssh_key', 'config', 'load', 'status', 'package', 'online', 'rooms', 'installed')

    @staticmethod
    def get_load(server):
        status = Status.objects.filter(server=server).last()
        return status and status.cpu_usage > 80

    @staticmethod
    def get_status(server):
        status = Status.objects.filter(
            server=server, created_at__gte=(now() - datetime.timedelta(minutes=10))
        ).first()
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
            return False

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
        fields = ('id', 'name', 'created_at', 'master', 'master_size')

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
        fields = ('id', 'name', 'created_at', 'spawner', 'room', 'spawner_size', 'room_size')

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
