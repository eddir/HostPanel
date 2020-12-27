import os
from abc import ABC
from pprint import pprint

from django.db.migrations import serializer
from rest_framework import serializers

from panel.models import Server, ServerStatus, Package


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'name', 'ip', 'user_root', 'password_root', 'user_single', 'password_single', 'ssh_key')


class PackageSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ('id', 'name', 'type', 'created_at', 'archive', 'size')

    def get_size(self, obj):
        pprint(obj)
        return os.path.getsize(obj.archive.path)


class ServerStatusSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(queryset=Server.objects.all())

    class Meta:
        model = ServerStatus
        fields = ('server', 'cpu_usage', 'ram_usage', 'ram_available', 'hdd_usage', 'hdd_available')

        def create(self, validated_data):
            return ServerStatus.objects.create(**validated_data)
