from django.contrib import admin

from .models import Server, Status, MPackage, SRPackage, Online, Dedic

admin.site.register(Dedic)
admin.site.register(Server)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


@admin.register(Online)
class OnlineAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


@admin.register(MPackage)
class MPackageAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)


@admin.register(SRPackage)
class SRPackageAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
