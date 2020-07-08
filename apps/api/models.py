from django.db import models

from ..user.models import User


class Controller(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='controller_online')
    callsign = models.CharField(max_length=16)
    frequency = models.FloatField()
    online_since = models.DateTimeField()
    last_update = models.DateTimeField()

    def return_duration(self):
        return self.last_update - self.online_since

    def __str__(self):
        return f'{self.user.return_full_name()} on {self.callsign}'


class ControllerSession(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='controller_sessions')
    callsign = models.CharField(max_length=16)
    time_logon = models.DateTimeField()
    duration = models.DurationField()

    def __str__(self):
        return f'{self.time_logon} | {self.user.return_full_name()} on {self.callsign}'
