import json

from django.db import models

from ..user.models import User


class Event(models.Model):
    name = models.CharField(max_length=128)
    banner = models.URLField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    host = models.CharField(max_length=16)
    description = models.TextField(null=True, blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class EventPosition(models.Model):
    event = models.ForeignKey(Event, models.CASCADE, related_name='positions')
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True, related_name='event_positions')
    name = models.CharField(max_length=16)

    @property
    def category(self):
        if '_DEL' in self.name or '_GND' in self.name or '_TWR' in self.name:
            return 'cab'
        elif 'APP' in self.name or '_DEP' in self.name:
            return 'tracon'
        else:
            return 'center'

    def __str__(self):
        return f'{self.event.name} | {self.name}'


class EventPositionRequest(models.Model):
    position = models.ForeignKey(EventPosition, models.CASCADE, related_name='requests')
    user = models.ForeignKey(User, models.CASCADE, related_name='event_requests')

    def assign(self):
        self.position.user = self.user
        self.position.save()


class PositionPreset(models.Model):
    name = models.CharField(max_length=32)
    positions_json = models.TextField(default='[]')

    @property
    def positions(self):
        return json.loads(self.positions_json)

    def set_positions(self, positions):
        self.positions_json = json.dumps(positions)

    def add_to_event(self, event):
        for position in self.positions:
            EventPosition(
                event=event,
                user=None,
                name=position,
            ).save()

    def __str__(self):
        return self.name


class EventScore(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='event_scores')
    event = models.ForeignKey(Event, models.CASCADE, related_name='scores')
    score = models.IntegerField()
