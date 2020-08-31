from django.contrib import admin
from .models import Event, EventPosition, PositionPreset, EventPositionRequest

admin.site.register(Event)
admin.site.register(EventPosition)
admin.site.register(EventPositionRequest)
admin.site.register(PositionPreset)
