import os

from django.db import models
from django.db.models import PROTECT
from django.dispatch import receiver

from HostPanel.settings import MEDIA_ROOT


class MPackage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    master = models.FileField(null=True)


class SRPackage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    spawner = models.FileField(null=True)
    room = models.FileField(null=True)


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


class Server(models.Model):
    name = models.CharField('Server name', max_length=32)
    ip = models.GenericIPAddressField('Ip address')
    user_root = models.CharField('Name of root user', max_length=32)
    user_single = models.CharField('Name of working user', max_length=32)
    password_root = models.CharField(max_length=32)
    password_single = models.CharField(max_length=32, blank=True)
    ssh_key = models.BooleanField('Connect via ssh key')
    log = models.TextField(null=True, blank=True, default=None)
    m_package = models.ForeignKey(MPackage, on_delete=PROTECT)
    sr_package = models.ForeignKey(SRPackage, on_delete=PROTECT)

    def __str__(self):
        return self.name


class ServerStatus(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    cpu_usage = models.SmallIntegerField()
    ram_usage = models.IntegerField()
    ram_available = models.IntegerField()
    hdd_usage = models.IntegerField()
    hdd_available = models.IntegerField()

    class Meta:
        verbose_name_plural = "Server status"

