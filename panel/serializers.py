import datetime
import os
from abc import ABC
from pprint import pprint

from django.template.defaultfilters import filesizeformat
from django.utils.timezone import now
from rest_framework import serializers

from panel.models import Server, ServerStatus, MPackage, SRPackage, SubServerStatus


class ServerSerializer(serializers.ModelSerializer):
    load = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = ('id', 'parent', 'name', 'ip', 'user_root', 'password_root', 'user_single', 'password_single',
                  'ssh_key', 'config', 'load', 'online', 'package')

    @staticmethod
    def get_load(server):
        status = ServerStatus.objects.filter(server=server).last()
        return status and status.cpu_usage > 80

    @staticmethod
    def get_online(server):
        return ServerStatus.objects.filter(server=server, created_at__gte=(now() - datetime.timedelta(minutes=10))) \
            .exists()


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


class ServerStatusSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(queryset=Server.objects.all())

    class Meta:
        model = ServerStatus
        fields = ('server', 'cpu_usage', 'ram_usage', 'ram_available', 'hdd_usage', 'hdd_available', 'online')


class SubServerStatusSerializer(serializers.ModelSerializer):
    server_status = serializers.PrimaryKeyRelatedField(queryset=ServerStatus.objects.all())

    class Meta:
        model = SubServerStatus
        fields = ('server_status', 'port', 'online', 'max_online')
