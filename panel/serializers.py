import datetime
import os
from abc import ABC
from pprint import pprint

from django.db.migrations import serializer
from django.utils.timezone import now
from rest_framework import serializers

from panel.models import Server, ServerStatus, MPackage, SRPackage


class ServerSerializer(serializers.ModelSerializer):
    load = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = ('id', 'name', 'ip', 'user_root', 'password_root', 'user_single', 'password_single', 'ssh_key',
                  'm_package', 'sr_package', 'load', 'online')

    def get_load(self, server):
        status = ServerStatus.objects.filter(server=server).last()
        return status and status.cpu_usage > 80

    def get_online(self, server):
        return ServerStatus.objects.filter(server=server, created_at__gte=(now()-datetime.timedelta(minutes=10))).exists()


class MPackageSerializer(serializers.ModelSerializer):
    master_size = serializers.SerializerMethodField()

    class Meta:
        model = MPackage
        fields = ('id', 'name', 'created_at', 'master', 'master_size')

    def get_master_size(self, package):
        return os.path.getsize(package.master.path)

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

    def get_spawner_size(self, package):
        return os.path.getsize(package.spawner.path)

    def get_room_size(self, package):
        return os.path.getsize(package.room.path)

    def to_representation(self, instance):
        representation = super(SRPackageSerializer, self).to_representation(instance)
        representation['created_at'] = instance.created_at.strftime("%d.%m.%Y %H:%M:%S")
        return representation


class ServerStatusSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(queryset=Server.objects.all())

    class Meta:
        model = ServerStatus
        fields = ('server', 'cpu_usage', 'ram_usage', 'ram_available', 'hdd_usage', 'hdd_available')

        def create(self, validated_data):
            return ServerStatus.objects.create(**validated_data)
