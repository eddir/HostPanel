import datetime
from pprint import pprint

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import DeleteView, UpdateView, DetailView, ListView

from panel import tasks
from panel.forms import ServerForm, ServerModelForm
from panel.models import Status, Server


class ServerListView(ListView):
    model = Server
    template_name = "panel/index.html"


class ServerDetailView(DetailView):
    model = Server


class ServerUpdate(UpdateView):
    model = Server
    fields = '__all__'
    success_url = reverse_lazy('panel:index')


class ServerDelete(DeleteView):
    model = Server
    success_url = reverse_lazy('panel:index')

    def get_context_data(self, **kwargs):
        context = super(ServerDelete, self).get_context_data(**kwargs)
        context['children'] = context['server'].parent is None and Server.objects.filter(
            parent=context['server'].id).exists()

        return context


def delete_server(request, pk):
    tasks.server_task(pk, "delete")
    return redirect('panel:index')


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
            tasks.server_task(server.id, "init")

            return HttpResponseRedirect('/')
    else:
        form = ServerForm()

    return render(request, 'panel/index.html', {'form': form})


class DedicatedView(ListView):
    model = Server
    template_name = "panel/dedicated.html"
