from django.urls import path

from .views.api.dedic import DedicView, DedicInstanceView, ReconnectDedic
from .views.api.package import PackageView, PackageInstanceView
from .views.api.server import ServerView, ForgetServer, DestroyServer, ServerInstanceView, StartServer, \
    StopServer, UpdateConfig, RebootServer, UpdateCaretaker, SetStatus
from .views.api.stat import OnlineView, StatusView, TaskView, VersionView, LegacyStatusView, PingView
from .views.api.users import UsersView
from .views.api.watchdog import LogsView, LogsDownloadView, LogsRemoveView
from .views.package import *
from .views.server import *
from .views.webhook import WebhookPush

app_name = 'panel'

urlpatterns = [
    path('webhook/', WebhookPush.as_view()),

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

    # API

    path('api/dedics/', DedicView.as_view()),
    path('api/dedic/<int:pk>/', DedicInstanceView.as_view()),
    path('api/dedic/<int:pk>/reconnect/', ReconnectDedic.as_view()),

    path('api/servers/', ServerView.as_view()),

    path('api/servers/status/', LegacyStatusView.as_view()),
    path('api/v2/servers/status/', StatusView.as_view()),
    path('api/servers/online/', OnlineView.as_view()),

    path('api/server/<int:pk>/', ServerInstanceView.as_view()),
    path('api/server/<int:pk>/start/', StartServer.as_view()),
    path('api/server/<int:pk>/stop/', StopServer.as_view()),
    path('api/server/<int:pk>/remove/', DestroyServer.as_view()),
    path('api/server/<int:pk>/remove/force/', ForgetServer.as_view()),
    path('api/server/<int:pk>/reboot/', RebootServer.as_view()),
    path('api/server/<int:pk>/config/', UpdateConfig.as_view()),
    path('api/server/<int:pk>/updateCaretaker/', UpdateCaretaker.as_view()),
    path('api/server/<int:pk>/setStatus/', SetStatus.as_view()),

    path('api/package/<str:package_type>/', PackageView.as_view()),
    path('api/package/<str:package_type>/<int:pk>/', PackageInstanceView.as_view()),
    path('api/package/<str:package_type>/<int:pk>/install/', PackageInstanceView.as_view()),

    path('api/task/', TaskView.as_view()),

    path('api/users/', UsersView.as_view()),

    path('api/version/', VersionView.as_view()),

    path('api/ping/', PingView.as_view()),

    path('api/watchdog/logs/<int:pk>/', LogsView.as_view()),
    path('api/watchdog/logs/<int:pk>/download/<str:file>/', LogsDownloadView.as_view()),
    path('api/watchdog/logs/<int:pk>/remove/<str:file>/', LogsRemoveView.as_view())
]
