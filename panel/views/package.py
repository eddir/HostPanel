from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView

from panel.models import Package


class PackageListView(ListView):
    model = Package
    template_name = "panel/package.html"


class PackageDelete(DeleteView):
    model = Package
    success_url = reverse_lazy('panel:packages')
