from django.contrib import admin

from .models import Server, ServerStatus

admin.site.register(Server)


@admin.register(ServerStatus)
class ServerStatusAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
