from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class SprayOperator(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255, db_index=1)
    team_leader = models.ForeignKey('TeamLeader', null=True)
    team_leader_assistant = models.ForeignKey('TeamLeaderAssistant', null=True)
    data_quality_check = models.BooleanField(default=False)
    average_spray_quality_score = models.FloatField(default=0.0)

    class Meta:
        app_label = 'main'

    def __str__(self):
        return '{}'.format(self.name)


class SprayOperatorDailySummary(models.Model):
    spray_form_id = models.CharField(max_length=50)
    submission_id = models.PositiveIntegerField(unique=True)
    sprayed = models.IntegerField()
    found = models.IntegerField()
    sprayoperator_code = models.CharField(max_length=10)
    data = JSONField(default={})
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'main'


class DirectlyObservedSprayingForm(models.Model):
    submission_id = models.PositiveIntegerField(unique=True)
    # max_length to 5 because they are yes/no answers
    correct_removal = models.CharField(max_length=5)
    correct_mix = models.CharField(max_length=5)
    rinse = models.CharField(max_length=5)
    PPE = models.CharField(max_length=5)
    CFV = models.CharField(max_length=5)
    correct_covering = models.CharField(max_length=5)
    leak_free = models.CharField(max_length=5)
    correct_distance = models.CharField(max_length=5)
    correct_speed = models.CharField(max_length=5)
    correct_overlap = models.CharField(max_length=5)

    district = models.CharField(max_length=10)
    health_facility = models.CharField(max_length=50)
    supervisor_name = models.CharField(max_length=10)
    sprayop_code_name = models.CharField(max_length=10)
    tl_code_name = models.CharField(max_length=10)
    data = JSONField(default={})
    spray_date = models.CharField(max_length=10)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'main'
