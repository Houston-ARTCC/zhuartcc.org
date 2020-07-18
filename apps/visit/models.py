from django.db import models


# Defines the visiting request model which is created upon request submission
class Visit(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    cid = models.IntegerField()
    email = models.EmailField()
    home_facility = models.CharField(max_length=32)
    rating = models.CharField(max_length=32)
    reason = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
