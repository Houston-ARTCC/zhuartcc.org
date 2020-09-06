from django.contrib import admin
from .models import Event, EventPosition, PositionPreset, EventPositionRequest, EventScore


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'start', 'end', 'hidden')


@admin.register(EventPosition)
class EventPositionAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'name')


@admin.register(EventPositionRequest)
class EventPositionRequestAdmin(admin.ModelAdmin):
    list_display = ('position', 'user')


@admin.register(PositionPreset)
class PositionPresetAdmin(admin.ModelAdmin):
    list_display = ('name', 'positions_json')


@admin.register(EventScore)
class EventScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'score')
