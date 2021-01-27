from django import forms
from django.forms import ModelForm

from panel.models import Server


class ServerForm(forms.Form):
    name = forms.CharField(label="Название сервера", required=True)
    ip = forms.GenericIPAddressField(label="IP адрес или домен", required=True)
    user_root = forms.CharField(label="Логин от рут пользователя", required=True)
    user_single = forms.CharField(label="Логин от обычного пользователя", required=True)
    password_root = forms.CharField(label="Пароль от рут пользователя", required=True)
    ssh_key = forms.BooleanField(label="Подключаться через ssh ключ или пароль", required=True)
    config = forms.CharField(label="Содержимое файла application.cfg", required=True)

    def add_server(self):
        pass


class ServerModelForm(ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'ip', 'user_root', 'user_single', 'password_root', 'ssh_key', 'config']
