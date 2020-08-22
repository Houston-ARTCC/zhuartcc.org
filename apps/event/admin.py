from django.contrib import admin
from .models import Event, EventPosition, PositionPreset

admin.site.register(Event)
admin.site.register(EventPosition)
admin.site.register(PositionPreset)
