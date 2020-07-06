from django.db import models

from ..user.models import User


class Controller(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='controller_online')
    position = models.CharField(max_length=16)
    freq = models.FloatField()
    time_logon = models.DateTimeField()


class ControllerSession(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='controller_sessions')
    position = models.CharField(max_length=16)
    time_logon = models.DateTimeField()
    duration = models.DurationField()
