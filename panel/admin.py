from django.contrib import admin

from .models import Server, ServerStatus, Package

admin.site.register(Server)


@admin.register(ServerStatus)
class ServerStatusAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
