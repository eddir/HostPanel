from django.contrib import admin

from .models import Server, ServerStatus, MPackage, SRPackage, SubServerStatus

admin.site.register(Server)


@admin.register(ServerStatus)
class ServerStatusAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


@admin.register(SubServerStatus)
class SubServerStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(MPackage)
class MPackageAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


@admin.register(SRPackage)
class SRPackageAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
