from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, FormView, CreateView

from panel.forms import ServerForm
from panel.models import Server


class ServerListView(ListView):
    model = Server
    template_name = "panel/index.html"


class ServerCreate(CreateView):
    model = Server
    fields = ['name', 'ip', 'user_root', 'user_single', 'password_root', 'password_single']
