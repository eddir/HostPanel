# Generated by Django 3.1.7 on 2021-03-21 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0017_dedic_last_listen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dedic',
            name='last_listen',
            field=models.DateTimeField(null=True),
        ),
    ]