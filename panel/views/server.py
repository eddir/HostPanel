import datetime
from pprint import pprint

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import DeleteView, UpdateView, DetailView, ListView

from panel import tasks
from panel.forms import ServerForm, ServerModelForm, DedicModelForm, DedicForm
from panel.models import Status, Server, Dedic


class ServerListView(ListView):
    """Index. Отсюда начинается использование панели."""
    model = Server
    template_name = "panel/index.html"


class ServerDetailView(DetailView):
    """Страница с детальной информацией о сервере."""
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
    if request.method == 'POST':
        tasks.server_task(pk, "delete")
        return redirect('panel:index')
    elif request.method == 'DELETE':
        Server.objects.get(pk=pk).delete()
        return HttpResponse(200)


class DedicDelete(DeleteView):
    model = Dedic
    success_url = reverse_lazy('panel:index')

    def get_context_data(self, **kwargs):
        context = super(DedicDelete, self).get_context_data(**kwargs)
        return context


def delete_dedic(request, pk):
    tasks.dedic_task(pk, "delete")
    return redirect('panel:dedicated')


def reconnect_dedic(request, pk):
    tasks.dedic_task(pk, "reconnect")
    return redirect('panel:dedicated')


def create_dedic(request):
    if request.method == 'POST':
        form = DedicModelForm(request.POST)

        if form.is_valid():
            dedic = Dedic(name=form.cleaned_data['name'],
                          ip=form.cleaned_data['ip'],
                          user_root=form.cleaned_data['user_root'],
                          user_single=form.cleaned_data['user_single'],
                          password_root=form.cleaned_data['password_root'])
            dedic.save()
            # tasks.server_task(dedic.id, "init")

            return HttpResponseRedirect('/')
    else:
        form = DedicForm()

    return render(request, 'panel/index.html', {'form': form})


class DedicatedView(ListView):
    model = Dedic
    template_name = "panel/dedicated.html"


class DedicEdit(UpdateView):
    model = Dedic
    fields = ['name']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('panel:dedicated')

    def form_valid(self, form):
        redirect_url = super(DedicEdit, self).form_valid(form)
        package = Dedic.objects.get(pk=self.kwargs['pk'])
        package.save()
        return redirect_url
