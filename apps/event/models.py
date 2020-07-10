from django.db import models

from ..user.models import User


class Event(models.Model):
    name = models.CharField(max_length=128)
    banner = models.URLField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.start.strftime("%b %d, %Y @ %H%Mz")} | {self.name}'


class EventPosition(models.Model):
    event = models.ForeignKey(Event, models.CASCADE, related_name='event_positions')
    user = models.ForeignKey(User, models.SET_NULL, null=True, related_name='event_positions', blank=True)
    position = models.CharField(max_length=16)

    def __str__(self):
        return f'{self.event.name} | {self.position}'
