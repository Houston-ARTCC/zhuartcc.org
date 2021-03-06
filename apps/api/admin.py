from django.contrib import admin
from .models import Controller, ControllerSession, CurrentAtis, TMUNotice


@admin.register(Controller)
class ControllerAdmin(admin.ModelAdmin):
    list_display = ('user', 'callsign', 'online_since', 'last_update', 'duration')


@admin.register(ControllerSession)
class ControllerSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'callsign', 'start', 'duration')


@admin.register(CurrentAtis)
class CurrentAtisAdmin(admin.ModelAdmin):
    list_display = ('facility', 'atis_letter', 'config_profile', 'updated')


@admin.register(TMUNotice)
class TMUNoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'time_issued', 'time_expires')
