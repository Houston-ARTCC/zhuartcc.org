from django.db import models

from apps.user.models import User


class ActionLog(models.Model):
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.timestamp} | {self.action}'


class Announcement(models.Model):
    author = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='announcements')
    subject = models.CharField(max_length=64)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'"{self.subject}" by {self.author.full_name}'
