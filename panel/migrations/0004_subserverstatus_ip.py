# Generated by Django 3.1.4 on 2021-02-17 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0003_auto_20210216_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='subserverstatus',
            name='ip',
            field=models.GenericIPAddressField(default='127.0.0.1'),
            preserve_default=False,
        ),
    ]
