from django.db import models


# Defines the visiting request model which is created upon request submission
from apps.user.models import User
from apps.user.updater import assign_oper_init


class Visit(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    cid = models.IntegerField()
    email = models.EmailField()
    home_facility = models.CharField(max_length=32)
    rating = models.CharField(max_length=32)
    reason = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)

    def add_to_roster(self):
        new_user = User(
            first_name=self.first_name.capitalize(),
            last_name=self.last_name.capitalize(),
            cid=self.cid,
            email=self.email,
            oper_init=assign_oper_init(self.first_name[0], self.last_name[0]),
            home_facility=self.home_facility,
            rating=self.rating,
            main_role='VC',
        )
        new_user.assign_initial_cert()
        new_user.save()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name
