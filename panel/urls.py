from django.urls import path

from . import views
from .views import ServerCreate

app_name = 'panel'

urlpatterns = [
    path('', views.ServerListView.as_view(), name='index'),
    path('server/add/', ServerCreate.as_view(), name="server.add"),
]