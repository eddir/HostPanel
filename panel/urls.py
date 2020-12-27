from django.urls import path

from .views.api import *
from .views.package import *
from .views.server import *


app_name = 'panel'

urlpatterns = [
    path('', ServerListView.as_view(), name='index'),
    path('server/<int:pk>/', ServerDetailView.as_view(), name="server.view"),
    path('server/add/', create_server, name="server.add"),
    path('packages/', PackageListView.as_view(), name='packages'),
]

urlpatterns += [
    path('server/<int:pk>/update/', ServerUpdate.as_view(), name='server.update'),
    path('server/<int:pk>/delete/', ServerDelete.as_view(), name='server.delete'),
    path('package/<int:pk>/delete/', PackageDelete.as_view(), name='package.delete'),
]

urlpatterns += [
    path('api/servers/', ServerView.as_view()),
    path('api/servers/status/', ServerStatusView.as_view()),
    path('api/server/<int:pk>/', ServerInstanceView.as_view()),
    path('api/server/<int:pk>/online', ServerOnlineView.as_view()),
    path('api/package/', PackageView.as_view()),
    path('api/package/<int:pk>/', PackageInstanceView.as_view()),
]
