from django.db import models


class EnrouteFlight(models.Model):
    # 3
    callsign = models.CharField(max_length=255)
    # 4
    aircraft = models.CharField(max_length=255)
    # 5
    tas_filed = models.IntegerField(null=True, blank=True)
    # 8
    tas_actual = models.IntegerField(null=True, blank=True)
    # 11
    prev_fix = models.CharField(max_length=255, null=True, blank=True)
    # 12
    prev_fix_time = models.IntegerField(null=True, blank=True)
    # 13
    prev_fix_time_rev = models.IntegerField(null=True, blank=True)
    # 14
    prev_fix_time_actual = models.IntegerField(null=True, blank=True)
    # 14a
    post_fix_plus = models.IntegerField(null=True, blank=True)
    # 15
    post_fix_time = models.IntegerField(null=True, blank=True)
    # 18
    post_fix_time_actual = models.IntegerField(null=True, blank=True)
    # 19
    post_fix = models.CharField(max_length=255, null=True, blank=True)
    # 20
    altitude = models.IntegerField(null=True, blank=True)
    # 21
    next_fix = models.CharField(max_length=255, null=True, blank=True)
    # 22
    next_fix_time = models.IntegerField(null=True, blank=True)
    # 23
    arrival = models.BooleanField()
    # 24
    requested_altitude = models.IntegerField(null=True, blank=True)
    # 25
    route = models.TextField(null=True, blank=True)
    # 27
    transponder = models.IntegerField(null=True, blank=True)

    coast = models.BooleanField(default=False)
    discarded = models.BooleanField(default=False)

    def __str__(self):
        return self.callsign
