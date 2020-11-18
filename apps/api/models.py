from django.db import models

from ..user.models import User


class Controller(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='controller_online')
    callsign = models.CharField(max_length=16)
    frequency = models.FloatField()
    online_since = models.DateTimeField()
    last_update = models.DateTimeField()

    @property
    def duration(self):
        return self.last_update - self.online_since

    def __str__(self):
        return f'{self.user.full_name} on {self.callsign}'


class ControllerSession(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='controller_sessions')
    callsign = models.CharField(max_length=16)
    start = models.DateTimeField()
    duration = models.DurationField()

    @property
    def end(self):
        return self.start + self.duration

    def __str__(self):
        return f'{self.start} | {self.user.full_name} on {self.callsign}'


class CurrentAtis(models.Model):
    facility = models.CharField(max_length=4)
    config_profile = models.CharField(max_length=16)
    atis_letter = models.CharField(max_length=1)
    airport_conditions = models.TextField()
    notams = models.TextField()
    updated = models.DateTimeField(auto_now=True)

class TMUNotice(models.Model):
    info = models.CharField(max_length=300)
    time_issued = models.CharField(max_length=5)