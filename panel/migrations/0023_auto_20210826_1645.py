# Generated by Django 3.2.6 on 2021-08-26 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0022_auto_20210825_0826'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPackage',
            fields=[
                ('package_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='panel.package')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=32)),
                ('archive', models.FileField(upload_to='packages')),
            ],
            bases=('panel.package',),
        ),
        migrations.AddField(
            model_name='server',
            name='custom',
            field=models.BooleanField(default=False),
        ),
    ]
