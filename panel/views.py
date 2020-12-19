from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, FormView, CreateView, DetailView, UpdateView, DeleteView
from rest_framework.response import Response
from rest_framework.views import APIView

from panel import tasks
from panel.forms import ServerForm, ServerModelForm
from panel.models import Server, ServerStatus
from panel.serializers import ServerSerializer, ServerStatusSerializer
from panel.tasks import init_server


class ServerListView(ListView):
    model = Server
    template_name = "panel/index.html"


class ServerDetailView(DetailView):
    model = Server

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = ServerStatus.objects.filter(server=self.object).last()
        return context


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
            init_server(server.id)

            return HttpResponseRedirect('/')
    else:
        form = ServerForm()

    return render(request, 'panel/index.html', {'form': form})


def start_server(request, pk):
    try:
        msg = tasks.start_server(pk)
    except Exception as e:
        msg = str(e)

    return HttpResponse(msg)


def stop_server(request, pk):
    try:
        msg = tasks.stop_server(pk)
    except Exception as e:
        msg = str(e)

    return HttpResponse(msg)


class ServerView(APIView):

    def get(self, request):
        servers = Server.objects.all()
        serializer = ServerSerializer(servers, many=True)
        return Response({"servers": serializer.data})

    def post(self, request):
        server = request.data
        serializer = ServerSerializer(data=server)
        server_saved = None

        if serializer.is_valid(raise_exception=True):
            server_saved = serializer.save()
            init_server(server_saved.id)

        return Response({"success": "Сервер '{}' добавлен.".format(server_saved.name)})


@method_decorator(csrf_exempt, name='dispatch')
class ServerStatusView(APIView):

    def get(self, request):
        stats = ServerStatus.objects.all()
        serializer = ServerSerializer(stats, many=True)
        return Response({"stats": serializer.data})

    def post(self, request):
        stats = request.data
        serializer = ServerStatusSerializer(data=stats)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Статус сервера обновлён."})
