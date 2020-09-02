from django.contrib import admin
from .models import ActionLog, Announcement

admin.site.register(ActionLog)
admin.site.register(Announcement)
