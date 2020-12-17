from abc import ABC

from django.db.migrations import serializer
from rest_framework import serializers

from panel.models import Server, ServerStatus


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'name', 'ip', 'user_root', 'password_root', 'user_single', 'password_single')


class ServerStatusSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(queryset=Server.objects.all())

    class Meta:
        model = ServerStatus
        fields = ('server', 'cpu_usage', 'ram_usage', 'ram_available', 'hdd_usage', 'hdd_available')

        def create(self, validated_data):
            return ServerStatus.objects.create(**validated_data)
