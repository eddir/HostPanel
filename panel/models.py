import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import PROTECT
from django.dispatch import receiver


class Package(models.Model):
    pass


class MPackage(Package):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    master = models.FileField(null=True, upload_to='packages')


class SRPackage(Package):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    spawner = models.FileField(null=True, upload_to='packages')
    room = models.FileField(null=True, upload_to='packages')


@receiver(models.signals.post_delete, sender=MPackage)
def auto_delete_file_on_delete_package(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Package` object is deleted.
    """
    if instance.master and os.path.isfile(instance.master.path):
        os.remove(instance.master.path)


@receiver(models.signals.post_delete, sender=SRPackage)
def auto_delete_file_on_delete_package(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Package` object is deleted.
    """
    for archive in [instance.spawner, instance.room]:
        if archive and os.path.isfile(archive.path):
            os.remove(archive.path)


class Dedic(models.Model):
    name = models.CharField('Dedic name', max_length=32, null=True)
    ip = models.GenericIPAddressField('Ip address')
    user_root = models.CharField('Name of root user', max_length=32, null=True)
    user_single = models.CharField('Name of working user', max_length=32, null=True)
    password_root = models.CharField(max_length=32)
    password_single = models.CharField(max_length=32, blank=True)
    ssh_key = models.BooleanField('Connect via ssh key')
    log = models.TextField(null=True, blank=True, default=None)


class Server(models.Model):
    parent = models.ForeignKey('Server', on_delete=models.CASCADE, null=True, blank=True)
    dedic = models.ForeignKey('Dedic', on_delete=models.RESTRICT)
    name = models.CharField('Server name', max_length=32)
    log = models.TextField(null=True, blank=True, default=None)
    config = models.TextField(null=True, blank=True, default=None)
    package = models.ForeignKey(Package, on_delete=models.PROTECT)


class Status(models.Model):

    class Condition(models.TextChoices):
        INSTALLED = 'IN', 'Устаналивается'
        STARTS = 'ST', 'Запускается'
        RUNNING = 'RN', 'Запущен'
        PAUSED = 'PS', 'Останавливается'
        STOPPED = 'SP', 'Остановлен'
        TERMINATED = 'TR', 'Удаляется'
        DELETED = 'DL', 'Удалён'
        REBOOT = 'RB', 'Ребут'

    created_at = models.DateTimeField(auto_now_add=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    condition = models.CharField(
        max_length=2,
        choices=Condition.choices,
        default=Condition.RUNNING,
    )
    cpu_usage = models.SmallIntegerField(null=True)
    ram_usage = models.BigIntegerField(null=True)
    ram_available = models.BigIntegerField(null=True)
    hdd_usage = models.BigIntegerField(null=True)
    hdd_available = models.BigIntegerField(null=True)

    class Meta:
        verbose_name_plural = "Server status"


class Online(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    port = models.SmallIntegerField(null=True, default=None)
    online = models.SmallIntegerField()
    max_online = models.SmallIntegerField(null=True, default=None)
