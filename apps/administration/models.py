from django.db import models

from apps.user.models import User


class ActionLog(models.Model):
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
