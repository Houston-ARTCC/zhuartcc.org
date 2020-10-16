from django.db import models
from ..user.models import User


TYPES = (
    (0, 'Classroom'),
    (1, 'Sweatbox'),
    (2, 'Online'),
    (3, 'OTS'),
)
LEVELS = (
    (0, 'Minor Ground'),
    (1, 'Major Ground'),
    (2, 'Minor Tower'),
    (3, 'Major Tower'),
    (4, 'Minor Approach'),
    (5, 'Major Approach'),
    (6, 'Center'),
    (7, 'Oceanic'),
)


class TrainingSession(models.Model):
    STATUSES = (
        (0, 'Scheduled'),
        (1, 'Completed'),
        (2, 'Cancelled'),
        (3, 'No-Show'),
    )
    OTS_STATUSES = (
        (0, 'Non-OTS'),
        (1, 'Passed'),
        (2, 'Failed'),
        (3, 'Recommended'),
    )
    student = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='student_sessions')
    instructor = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='instructor_sessions')
    start = models.DateTimeField()
    end = models.DateTimeField()
    movements = models.IntegerField(default=0)
    progress = models.IntegerField(default=3)
    position = models.CharField(max_length=16)
    type = models.IntegerField(choices=TYPES)
    level = models.IntegerField(choices=LEVELS)
    status = models.IntegerField(default=0, choices=STATUSES)
    ots_status = models.IntegerField(default=0, choices=OTS_STATUSES)
    ctrs_id = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    @property
    def duration(self):
        return self.end - self.start

    def __str__(self):
        return f'{self.start} | {self.student.full_name} with {self.instructor.full_name}'


class TrainingRequest(models.Model):
    student = models.ForeignKey(User, models.CASCADE, related_name='training_requests')
    start = models.DateTimeField()
    end = models.DateTimeField()
    type = models.IntegerField(choices=TYPES)
    level = models.IntegerField(choices=LEVELS)
    remarks = models.TextField(null=True, blank=True)

    @property
    def duration(self):
        return self.end - self.start

    def __str__(self):
        return f'{self.student.full_name} | Training request for {self.get_level_display()}'
