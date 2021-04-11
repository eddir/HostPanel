from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView, DetailView, ListView

from panel.tasks import tasks
from panel.models import Server, Dedic


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


def delete_dedic(request, pk):
    if not Server.objects.filter(dedic=pk).exists():
        tasks.dedic_task(pk, "delete")
    return HttpResponse(200)


def reconnect_dedic(request, pk):
    tasks.dedic_task(pk, "reconnect")
    return redirect('panel:dedicated')


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
