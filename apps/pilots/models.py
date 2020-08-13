from django.db import models


class Scenery(models.Model):
    SIMULATORS = (
        (0, 'Prepar3D / FSX'),
        (1, 'X-Plane')
    )
    simulator = models.IntegerField(choices=SIMULATORS)
    name = models.CharField(max_length=255)
    link = models.URLField()
    payware = models.BooleanField()
