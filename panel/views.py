from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, CreateView, DetailView, UpdateView, DeleteView

from panel.forms import ServerForm, ServerModelForm
from panel.models import Server


class ServerListView(ListView):
    model = Server
    template_name = "panel/index.html"


class ServerDetailView(DetailView):
    model = Server


class ServerCreate(CreateView):
    model = Server
    fields = ['name', 'ip', 'user_root', 'user_single', 'password_root']


class ServerUpdate(UpdateView):
    model = Server
    fields = '__all__'
    success_url = reverse_lazy('panel:index')


class ServerDelete(DeleteView):
    model = Server
    success_url = reverse_lazy('panel:index')


def create_server(request):
    if request.method == 'POST':
        form = ServerModelForm(request.POST)

        if form.is_valid():
            server = Server(name=form.cleaned_data['name'],
                            ip=form.cleaned_data['ip'],
                            user_root=form.cleaned_data['user_root'],
                            user_single=form.cleaned_data['user_single'],
                            password_root=form.cleaned_data['password_root'])
            server.save()

            return HttpResponseRedirect('/')
    else:
        form = ServerForm()

    return render(request, 'panel/index.html', {'form': form})
