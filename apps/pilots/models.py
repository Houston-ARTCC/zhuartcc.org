from django.db import models


class Scenery(models.Model):
    SIMULATORS = (
        ('P3D', 'Prepar3D / FSX'),
        ('XP', 'X-Plane')
    )
    simulator = models.CharField(max_length=8, choices=SIMULATORS)
    name = models.CharField(max_length=255)
    link = models.URLField()
    payware = models.BooleanField()
