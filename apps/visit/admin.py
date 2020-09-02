from django.contrib import admin
from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('cid', 'first_name', 'last_name', 'email', 'rating', 'submitted')
