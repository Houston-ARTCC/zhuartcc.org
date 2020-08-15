from django.db import models


class ActionLog(models.Model):
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
