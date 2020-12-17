from django.urls import path

from . import views
from .views import ServerCreate, ServerView, ServerStatusView

app_name = 'panel'

urlpatterns = [
    path('', views.ServerListView.as_view(), name='index'),
    path('server/<int:pk>/', views.ServerDetailView.as_view(), name="server.view"),
    path('server/add/', views.create_server, name="server.add"),
]

urlpatterns += [
    path('server/create/', views.ServerCreate.as_view(), name='server.create'),
    path('server/<int:pk>/update/', views.ServerUpdate.as_view(), name='server.update'),
    path('server/<int:pk>/delete/', views.ServerDelete.as_view(), name='server.delete'),
]

urlpatterns += [
    path('api/servers/', ServerView.as_view()),
    path('api/servers/status/', ServerStatusView.as_view()),
]
