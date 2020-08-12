import json
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
    level = models.IntegerField(choices=LEVELS)
    status = models.IntegerField(default=0, choices=STATUSES)
    session_notes = models.FileField(upload_to='training/', null=True, blank=True)

    def __str__(self):
        return f'{self.start} | {self.student.return_full_name()} with {self.instructor.return_full_name()}'


class Question(models.Model):
    CHOICES = (
        ('A', 'Choice 1'),
        ('B', 'Choice 2'),
        ('C', 'Choice 3'),
        ('D', 'Choice 4'),
    )
    question = models.CharField(max_length=255)
    image = models.ImageField(upload_to='exams', null=True, blank=True)
    choice_1 = models.CharField(max_length=255)
    choice_2 = models.CharField(max_length=255)
    choice_3 = models.CharField(max_length=255, null=True, blank=True)
    choice_4 = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=1, choices=CHOICES)

    def __str__(self):
        return self.question


class Exam(models.Model):
    student = models.ForeignKey(User, models.CASCADE, related_name='student_exams')
    name = models.CharField(max_length=255)
    questions = models.ManyToManyField(Question)
    answers = models.TextField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    assigned = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()
    submitted = models.DateTimeField(null=True, blank=True)

    def get_answers(self):
        return json.loads(self.answers)

    def score_exam(self):
        correct = 0
        answers = self.get_answers()
        for question in self.questions.all():
            if question.answer == answers[str(question.id)]:
                correct += 1
        self.score = (correct / self.questions.count()) * 100
        self.completed = True
        self.save()

    def __str__(self):
        return f'{self.assigned} | {self.student.return_full_name()} - {self.name}'
