from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, UpdateView

from panel import tasks
from panel.models import MPackage, SRPackage, Server


class MPackageListView(ListView):
    model = MPackage
    template_name = "panel/mpackage.html"


class MPackageDelete(DeleteView):
    model = MPackage
    success_url = reverse_lazy('panel:m_packages')


class MPackageEdit(UpdateView):
    model = MPackage
    fields = ['name', 'master']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('panel:m_packages')

    def form_valid(self, form):
        redirect_url = super(MPackageEdit, self).form_valid(form)
        package = MPackage.objects.get(pk=self.kwargs['pk'])
        package.save()

        for server in Server.objects.filter(m_package=package):
            tasks.update_server(server.id)

        return redirect_url


class SRPackageEdit(UpdateView):
    model = SRPackage
    fields = ['name', 'spawner', 'room']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('panel:sr_packages')

    def form_valid(self, form):
        redirect_url = super(SRPackageEdit, self).form_valid(form)
        package = SRPackage.objects.get(pk=self.kwargs['pk'])
        package.save()

        for server in Server.objects.filter(sr_package=package):
            tasks.update_server(server.id)

        return redirect_url


class SRPackageListView(ListView):
    model = SRPackage
    template_name = "panel/srpackage.html"


class SRPackageDelete(DeleteView):
    model = SRPackage
    success_url = reverse_lazy('panel:sr_packages')
