import json
from datetime import timedelta

from django.db import models

from ..api.models import ControllerSession, Controller
from ..user.models import User


class Event(models.Model):
    name = models.CharField(max_length=128)
    banner = models.URLField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    host = models.CharField(max_length=16)
    description = models.TextField(null=True, blank=True)
    hidden = models.BooleanField(default=False)
    scored = models.BooleanField(default=False)

    @property
    def duration(self):
        return self.end - self.start

    def calculate_scores(self):
        for position in self.positions.all():
            if position.user is not None:
                duration = timedelta()

                sessions = ControllerSession.objects.filter(user=position.user)
                for session in sessions:
                    if session.start < self.end and session.end > self.start:
                        duration += min([session.end, self.end]) - max([session.start, self.start])

                active_sessions = Controller.objects.filter(user=position.user)
                for session in active_sessions:
                    cleanup = self.end + timedelta(hours=1)
                    if session.online_since < cleanup and session.last_update > self.start:
                        duration += min([session.last_update, cleanup]) - max([session.online_since, self.start])

                session_seconds, event_seconds = duration.total_seconds(), self.duration.total_seconds()
                if session_seconds < event_seconds and event_seconds - session_seconds <= 120:
                    session_seconds = event_seconds

                score = [(session_seconds / event_seconds) * 100]
                comments = f'Controlled for <b>{duration}</b> out of ' \
                           f'<b>{self.duration}</b> event duration ({int(score[0])}%).'

                event_feedback = self.feedback.filter(controller=position.user)
                for feedback in event_feedback:
                    feedback_score = (feedback.rating / 5) * 100
                    score += [feedback_score]

                    color = "danger" if feedback.rating < 3 else "warning" if feedback.rating < 5 else "success"
                    comments += f'<br><b><span class="text-{color}">Feedback: {feedback.rating} / 5 ' \
                                f'({int(feedback_score)}%).</span></b>'

                EventScore(
                    user=position.user,
                    event=self,
                    score=int(sum(score) / len(score)),
                    comments=comments
                ).save()

        self.scored = True
        self.save()

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
        elif '_APP' in self.name or '_DEP' in self.name:
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
    comments = models.TextField(null=True, blank=True)
