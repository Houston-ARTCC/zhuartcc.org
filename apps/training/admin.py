from django.contrib import admin
from .models import TrainingSession, TrainingRequest


@admin.register(TrainingSession)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'instructor', 'start', 'type', 'level', 'status')


@admin.register(TrainingRequest)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'start', 'end', 'type', 'level')

