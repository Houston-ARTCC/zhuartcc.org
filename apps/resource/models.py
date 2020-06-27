from django.db import models


class Resource(models.Model):
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=64)
    path = models.FileField(upload_to='doc/')
    updated = models.DateTimeField()

    def __str__(self):
        return self.name
