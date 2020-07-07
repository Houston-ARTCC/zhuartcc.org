from datetime import datetime, timedelta
from django.db import models

from ..user.models import User


class Controller(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='controller_online')
    callsign = models.CharField(max_length=16)
    frequency = models.FloatField()
    online_since = models.DateTimeField()
    online_for = models.DurationField(default=timedelta(0))

    def update_duration(self):
        self.online_for = datetime.utcnow() - self.online_since
        return self.online_for


class ControllerSession(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='controller_sessions')
    callsign = models.CharField(max_length=16)
    time_logon = models.DateTimeField()
    duration = models.DurationField()
