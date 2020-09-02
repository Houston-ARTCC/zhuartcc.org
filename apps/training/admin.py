from django.contrib import admin
from .models import TrainingSession, TrainingRequest

admin.site.register(TrainingSession)
admin.site.register(TrainingRequest)
