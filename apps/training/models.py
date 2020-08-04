from datetime import timedelta
from django.db import models
from ..user.models import User


class TrainingSession(models.Model):
    TYPES = (
        (0, 'Classroom'),
        (1, 'Sweatbox'),
        (2, 'Online'),
        (3, 'OTS'),
    )
    STATUSES = (
        (0, 'Scheduled'),
        (1, 'Completed'),
        (2, 'Cancelled'),
        (3, 'No-Show'),
    )
    student = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='student_sessions')
    instructor = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='instructor_sessions')
    start = models.DateTimeField()
    duration = models.DurationField(default=timedelta(hours=1))
    position = models.CharField(max_length=16, null=True, blank=True)
    type = models.IntegerField(choices=TYPES)
    status = models.IntegerField(default=0, choices=STATUSES)
    session_notes = models.FileField(upload_to='training/', null=True, blank=True)

    def __str__(self):
        return f'{self.start} | {self.student.return_full_name()} with {self.instructor.return_full_name()}'


class ExamQuestion(models.Model):
    question = models.TextField()

    def __str__(self):
        return self.question


class Exam(models.Model):
    student = models.ForeignKey(User, models.CASCADE, related_name='student_exams')
    name = models.CharField(max_length=255)
    questions = models.ManyToManyField(ExamQuestion)
    assigned = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()
    score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.assigned} | {self.student.return_full_name()} - {self.name}'
