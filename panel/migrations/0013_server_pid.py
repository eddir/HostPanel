# Generated by Django 3.1.4 on 2021-03-02 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0012_auto_20210301_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='pid',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
    ]
