import datetime
import os

from background_task.models import Task
from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now


class Package(models.Model):
    pass


class MPackage(Package):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    master = models.FileField(upload_to='packages')
    bin_path = models.CharField(max_length=128)

    class Meta:
        ordering = ['-id']


class SRPackage(Package):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    spawner = models.FileField(upload_to='packages')
    room = models.FileField(upload_to='packages')
    bin_path = models.CharField(max_length=128)

    class Meta:
        ordering = ['-id']


class CPackage(Package):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32)
    archive = models.FileField(upload_to='packages')
    bin_path = models.CharField(max_length=128)


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
    condition = models.BooleanField(default=False)
    last_listen = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-id']


@receiver(models.signals.post_delete, sender=Dedic)
def auto_delete_tasks_on_delete_dedic(sender, instance, **kwargs):
    """
    Отменяем задачи, связанные с дедиком, которого уже нет вследствие его удаления.
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    Task.objects.filter(task_params__contains="[" + str(instance.id)).filter(task_name="panel.tasks.tasks.dedic_task")\
        .delete()


class Server(models.Model):
    custom = models.BooleanField(default=False)
    parent = models.ForeignKey('Server', on_delete=models.CASCADE, null=True, blank=True)
    dedic = models.ForeignKey('Dedic', on_delete=models.RESTRICT)
    name = models.CharField('Server name', max_length=32)
    log = models.TextField(null=True, blank=True, default=None)
    config = models.TextField(null=True, blank=True, default=None)
    package = models.ForeignKey(Package, on_delete=models.PROTECT)

    def get_last_status(self):
        return Status.objects.filter(
            server=self, created_at__gte=(now() - datetime.timedelta(minutes=10))
        ).first()

    def is_running(self):
        return self.get_last_status().condition == Status.Condition.RUNNING

    class Meta:
        ordering = ['-id']


@receiver(models.signals.post_delete, sender=Server)
def auto_delete_tasks_on_delete_server(sender, instance, **kwargs):
    """
    Отменяем задачи, связанные с сервером, которого уже нет вследствие его удаления.
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    Task.objects.filter(task_params__contains="[" + str(instance.id)).filter(task_name="panel.tasks.tasks.server_task")\
        .delete()


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

    mem_total = models.IntegerField(null=True)
    mem_available = models.IntegerField(null=True)

    disk_total = models.IntegerField(null=True)
    disk_available = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = "Server status"


class Online(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    port = models.SmallIntegerField(null=True, default=None)
    online = models.SmallIntegerField()
    max_online = models.SmallIntegerField(null=True, default=None)
