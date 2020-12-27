import os

from django.db import models
from django.dispatch import receiver

from HostPanel.settings import MEDIA_ROOT


class Server(models.Model):
    name = models.CharField('Server name', max_length=32)
    ip = models.GenericIPAddressField('Ip address')
    user_root = models.CharField('Name of root user', max_length=32)
    user_single = models.CharField('Name of working user', max_length=32)
    password_root = models.CharField(max_length=32)
    password_single = models.CharField(max_length=32, blank=True)
    ssh_key = models.BooleanField('Connect via ssh key')
    log = models.TextField(null=True, blank=True, default=None)

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


class Package(models.Model):

    class PackageTypes(models.TextChoices):
        MASTER = 0
        SPAWNER = 1
        ROOM = 2

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    type = models.PositiveSmallIntegerField(
        choices=PackageTypes.choices,
        default=PackageTypes.MASTER,
    )
    archive = models.FileField()


@receiver(models.signals.post_delete, sender=Package)
def auto_delete_file_on_delete_package(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Package` object is deleted.
    """
    if instance.archive:
        if os.path.isfile(instance.archive.path):
            os.remove(instance.archive.path)
        else:
            print("Не удалилось")
            print(MEDIA_ROOT + instance.archive.path)
