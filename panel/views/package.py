from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView

from panel.models import MPackage, SRPackage


class MPackageListView(ListView):
    model = MPackage
    template_name = "panel/mpackage.html"


class MPackageDelete(DeleteView):
    model = MPackage
    success_url = reverse_lazy('panel:m_packages')


class SRPackageListView(ListView):
    model = SRPackage
    template_name = "panel/srpackage.html"


class SRPackageDelete(DeleteView):
    model = SRPackage
    success_url = reverse_lazy('panel:sr_packages')
