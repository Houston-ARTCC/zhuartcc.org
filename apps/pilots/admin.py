from django.contrib import admin
from .models import Scenery


@admin.register(Scenery)
class SceneryAdmin(admin.ModelAdmin):
    list_display = ('name', 'simulator', 'payware', 'link')
