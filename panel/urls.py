from django.urls import path

from .views.api import *
from .views.package import *
from .views.server import *

app_name = 'panel'

urlpatterns = [
    # Основные ссылки
    path('', ServerListView.as_view(), name='index'),
    path('m_packages/', MPackageListView.as_view(), name='m_packages'),
    path('sr_packages/', SRPackageListView.as_view(), name='sr_packages'),
    path('dedicated/', DedicatedView.as_view(), name='dedicated'),
    path('server/<int:pk>/', ServerDetailView.as_view(), name="server.view"),

    # Действия с серверами
    path('server/<int:pk>/update/', ServerUpdate.as_view(), name='server.update'),
    path('server/<int:pk>/delete/', ServerDelete.as_view(), name='server.delete'),
    path('server/<int:pk>/delete/confirm/', delete_server, name='server.delete.confirm'),

    # Действия с дедиками
    path('dedic/<int:pk>/delete/confirm/', delete_dedic, name='dedic.delete.confirm'),
    path('dedic/<int:pk>/edit/', DedicEdit.as_view(), name='dedic.edit'),
    path('dedic/<int:pk>/reconnect/', reconnect_dedic, name='dedic.reconnect'),

    # Действия со сбокрами
    path('m_package/<int:pk>/delete/', MPackageDelete.as_view(), name='m_package.delete'),
    path('m_package/<int:pk>/edit/', MPackageEdit.as_view(), name='m_package.edit'),
    path('sr_package/<int:pk>/delete/', SRPackageDelete.as_view(), name='sr_package.delete'),
    path('sr_package/<int:pk>/edit/', SRPackageEdit.as_view(), name='sr_package.edit'),

    # AJAX

    path('api/dedics/', DedicView.as_view()),

    path('api/servers/', ServerView.as_view()),
    path('api/servers/status/', StatusView.as_view()),
    path('api/servers/online/', OnlineView.as_view()),
    path('api/server/<int:pk>/', ServerInstanceView.as_view()),
    path('api/server/<int:pk>/config', update_config),

    path('api/m_package/', MPackageView.as_view()),
    path('api/m_package/<int:pk>/', MPackageInstanceView.as_view()),
    path('api/m_package/<int:pk>/install/', MPackageInstanceView.as_view()),

    path('api/sr_package/<int:pk>/install/', SRPackageInstanceView.as_view()),
    path('api/sr_package/', SRPackageView.as_view()),

    path('api/task/', TaskPackageView.as_view()),
]
