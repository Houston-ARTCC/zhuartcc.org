from django.contrib import admin
from .models import Controller, ControllerSession


@admin.register(Controller)
class ControllerAdmin(admin.ModelAdmin):
    list_display = ('user', 'callsign', 'frequency', 'online_since', 'last_update', 'duration')


@admin.register(ControllerSession)
class ControllerSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'callsign', 'time_logon', 'duration')
