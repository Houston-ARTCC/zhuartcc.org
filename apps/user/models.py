from django.db import models


# Defines the User model which is created for all home and visiting controllers
class User(models.Model):
    # User Details
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    cid = models.IntegerField()
    email = models.EmailField()
    oper_init = models.CharField(max_length=32)
    home_facility = models.CharField(max_length=32, null=True, blank=True)
    rating = models.CharField(max_length=32)

    # ARTCC Roles
    main_role = models.CharField(max_length=32)
    staff_role = models.CharField(max_length=32, null=True, blank=True)
    training_role = models.CharField(max_length=32, null=True, blank=True)
    mentor_level = models.CharField(max_length=32, null=True, blank=True)

    # Endorsements
    cert_int = models.IntegerField(default=0)
    del_cert = models.IntegerField(default=0)
    gnd_cert = models.IntegerField(default=0)
    twr_cert = models.IntegerField(default=0)
    app_cert = models.IntegerField(default=0)
    ctr_cert = models.IntegerField(default=0)
    ocn_cert = models.IntegerField(default=0)
    solo_cert = models.CharField(max_length=32, null=True, blank=True)

    # Profile Details
    profile_picture = models.ImageField(null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    staff_comment = models.TextField(null=True, blank=True)
    staff_comment_author = models.ForeignKey('self', models.SET_NULL, null=True, blank=True)

    # Status
    status = models.IntegerField(default=0)
    loa_until = models.DateField(null=True, blank=True)
    loa_last_month = models.BooleanField(default=False)
    activity_exempt = models.BooleanField(default=False)

    # Returns boolean value representing whether or not the user is staff
    def is_staff(self):
        return self.staff_role is not None and self.staff_role != ''

    # Returns boolean value representing whether or not the user is a mentor or instructor
    def is_mentor(self):
        return self.training_role is not None and self.training_role != ''

    # Returns a string of the user's full name
    def return_full_name(self):
        return f'{self.first_name} {self.last_name}'

    # Returns an enumerated integer based on the user's endorsement level
    def return_cert_int(self):
        if self.ocn_cert == 2:
            return 8
        elif self.ctr_cert == 2:
            return 7
        elif self.app_cert == 2:
            return 6
        elif self.app_cert == 1 or self.app_cert == 3:
            return 5
        elif self.twr_cert == 2:
            return 4
        elif self.twr_cert == 1 or self.twr_cert == 3:
            return 3
        elif self.gnd_cert == 2:
            return 2
        elif self.gnd_cert == 1 or self.gnd_cert == 3:
            return 1
        else:
            return 0

    # Returns an enumerated integer based on the user's rating
    def return_rating_int(self):
        if self.rating == 'OBS':
            return 0
        elif self.rating == 'S1':
            return 1
        elif self.rating == 'S2':
            return 2
        elif self.rating == 'S3':
            return 3
        elif self.rating == 'C1':
            return 4
        elif self.rating == 'C3':
            return 5
        elif self.rating == 'I1':
            return 6
        elif self.rating == 'I3':
            return 7
        elif self.rating == 'SUP':
            return 8
        elif self.rating == 'ADM':
            return 9

    # Awards minor DEL, GND, TWR, and APP endorsement to S2+ controllers
    def assign_initial_cert(self):
        if self.return_rating_int() > 1:
            self.del_cert = 1
            self.gnd_cert = 1
            self.twr_cert = 1
        if self.return_rating_int() > 2:
            self.app_cert = 1
        self.cert_int = self.return_cert_int()

    def __str__(self):
        return f'({self.main_role}) {self.return_full_name()}'
