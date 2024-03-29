# Generated by Django 3.1.4 on 2021-02-17 17:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0006_subserverstatus_ip'),
    ]

    operations = [
        migrations.CreateModel(
            name='Online',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ip', models.GenericIPAddressField()),
                ('port', models.SmallIntegerField()),
                ('online', models.SmallIntegerField()),
                ('max_online', models.SmallIntegerField()),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel.server')),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cpu_usage', models.SmallIntegerField()),
                ('ram_usage', models.BigIntegerField()),
                ('ram_available', models.BigIntegerField()),
                ('hdd_usage', models.BigIntegerField()),
                ('hdd_available', models.BigIntegerField()),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel.server')),
            ],
            options={
                'verbose_name_plural': 'Server status',
            },
        ),
        migrations.RemoveField(
            model_name='subserverstatus',
            name='server_status',
        ),
        migrations.DeleteModel(
            name='ServerStatus',
        ),
        migrations.DeleteModel(
            name='SubServerStatus',
        ),
    ]
