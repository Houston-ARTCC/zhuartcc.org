from django.contrib import admin
from .models import TrainingSession, Exam, ExamQuestion

admin.site.register(TrainingSession)
admin.site.register(Exam)
admin.site.register(ExamQuestion)
