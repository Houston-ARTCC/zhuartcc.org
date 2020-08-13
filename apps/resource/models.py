from django.db import models


class Resource(models.Model):
    CATEGORIES = (
        ('VRC', 'VRC'),
        ('vSTARS', 'vSTARS'),
        ('vERAM', 'vERAM'),
        ('vATIS', 'vATIS'),
        ('SOP', 'SOP'),
        ('LOA', 'LOA'),
        ('MAVP', 'MAVP'),
        ('Misc', 'Misc')
    )
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=64, choices=CATEGORIES)
    path = models.FileField(upload_to='doc/')
    updated = models.DateTimeField()

    def __str__(self):
        return self.name
