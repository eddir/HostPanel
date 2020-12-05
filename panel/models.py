from django.db import models


class Server(models.Model):
    name = models.CharField('Server name', max_length=32)
    ip = models.GenericIPAddressField('Ip address')
    user_root = models.CharField('Name of root user', max_length=32)
    user_single = models.CharField('Name of working user', max_length=32)
    password_root = models.CharField(max_length=32)
    password_single = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.name
