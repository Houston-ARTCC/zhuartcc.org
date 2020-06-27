import datetime
from django.db import models
from ..user.models import User


class TrainingSession(models.Model):
    student = models.ForeignKey(User, models.SET_NULL, null=True, related_name='student_sessions')
    instructor = models.ForeignKey(User, models.SET_NULL, null=True, related_name='instructor_sessions')
    start = models.DateTimeField()
    duration = models.TimeField(default=datetime.time(hour=1))
    position = models.CharField(max_length=16, null=True)
    level = models.IntegerField()
    type = models.IntegerField()
    status = models.IntegerField()
    session_notes = models.FileField(upload_to='training/', null=True)
    ots_rec = models.BooleanField(default=False)
    ots_passed = models.BooleanField(default=False)

    # Returns string representation of session type
    def return_type_str(self):
        if self.type == 0:
            return 'Classroom'
        elif self.type == 1:
            return 'Sweatbox'
        elif self.type == 2:
            return 'Online'
        elif self.type == 3:
            return 'OTS'

    # Returns string representation of the session level
    def return_level_str(self):
        if self.level == 0:
            return 'Minor Delivery'
        elif self.level == 1:
            return 'Major Delivery'
        elif self.level == 2:
            return 'Minor Ground'
        elif self.level == 3:
            return 'Major Ground'
        elif self.level == 4:
            return 'Minor Tower'
        elif self.level == 5:
            return 'Major Tower'
        elif self.level == 6:
            return 'Minor Approach'
        elif self.level == 7:
            return 'Major Approach'
        elif self.level == 8:
            return 'Center'
        elif self.level == 9:
            return 'Oceanic'
