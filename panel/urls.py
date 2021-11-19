from django.urls import path

from .views.dedic import DedicView, DedicInstanceView, ReconnectDedic
from .views.package import PackageView, PackageInstanceView
from .views.server import ServerView, ForgetServer, DestroyServer, ServerInstanceView, StartServer, \
    StopServer, UpdateConfig, RebootServer, UpdateCaretaker, SetStatus
from .views.settings import TelegramSubscriptionsView, TelegramSubscriberView, VersionView, PingView
from .views.stat import OnlineView, StatusView, TaskView, LegacyStatusView
from .views.users import UsersView
from .views.watchdog import LogsView, LogsDownloadView, LogsRemoveView
from .views.webhook import WebhookPush

app_name = 'panel'

urlpatterns = [

    # GitHub webhooks

    path('webhook/', WebhookPush.as_view()),

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

    path('api/subscribers/', TelegramSubscriptionsView.as_view()),
    path('api/subscribers/<int:pk>/', TelegramSubscriberView.as_view()),

    path('api/watchdog/logs/<int:pk>/', LogsView.as_view()),
    path('api/watchdog/logs/<int:pk>/download/<str:file>/', LogsDownloadView.as_view()),
    path('api/watchdog/logs/<int:pk>/remove/<str:file>/', LogsRemoveView.as_view())
]
