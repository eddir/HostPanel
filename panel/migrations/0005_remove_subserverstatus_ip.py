# Generated by Django 3.1.4 on 2021-02-17 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0004_subserverstatus_ip'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subserverstatus',
            name='ip',
        ),
    ]
