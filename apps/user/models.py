from django.db import models


# Defines the User model which is created for all home and visiting controllers
class User(models.Model):
    STATUSES = (
        (0, 'Active'),
        (1, 'LOA'),
        (2, 'Inactive'),
    )
    ENDORSEMENTS = (
        (0, 'No Endorsement'),
        (1, 'Minor Endorsement'),
        (2, 'Major Endorsement'),
        (3, 'Solo Endorsement'),
    )
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
    del_cert = models.IntegerField(default=0, choices=ENDORSEMENTS)
    gnd_cert = models.IntegerField(default=0, choices=ENDORSEMENTS)
    twr_cert = models.IntegerField(default=0, choices=ENDORSEMENTS)
    app_cert = models.IntegerField(default=0, choices=ENDORSEMENTS)
    ctr_cert = models.IntegerField(default=0, choices=ENDORSEMENTS)
    ocn_cert = models.IntegerField(default=0, choices=ENDORSEMENTS)
    solo_cert = models.CharField(max_length=32, null=True, blank=True)

    # Profile Details
    profile_picture = models.ImageField(null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    staff_comment = models.TextField(null=True, blank=True)
    staff_comment_author = models.ForeignKey('self', models.SET_NULL, null=True, blank=True)

    # Status
    status = models.IntegerField(default=0, choices=STATUSES)
    loa_until = models.DateField(null=True, blank=True)
    loa_last_month = models.BooleanField(default=False)
    activity_exempt = models.BooleanField(default=False)
    prevent_event_signup = models.BooleanField(default=False)

    @property
    def event_score(self):
        if self.main_role == 'HC':
            scores = [100]
        else:
            scores = [85]
        scores += [score.score for score in self.event_scores.all()]
        return int(sum(scores) / len(scores))

    # Returns boolean value representing whether or not the user is staff
    @property
    def is_staff(self):
        return self.staff_role is not None and self.staff_role != ''

    # Returns boolean value representing whether or not the user is a mentor or instructor
    @property
    def is_mentor(self):
        return self.training_role is not None and self.training_role != ''

    # Returns a string of the user's full name
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    # Returns an enumerated integer based on the user's endorsement level
    @property
    def cert_int(self):
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
    @property
    def rating_int(self):
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
        self.del_cert = 0
        self.gnd_cert = 0
        self.twr_cert = 0
        self.app_cert = 0
        self.ctr_cert = 0
        self.ocn_cert = 0
        if self.rating_int > 1:
            self.del_cert = 1
            self.gnd_cert = 1
            self.twr_cert = 1
        if self.rating_int > 2:
            self.app_cert = 1
        self.save()

    def __str__(self):
        return self.full_name
