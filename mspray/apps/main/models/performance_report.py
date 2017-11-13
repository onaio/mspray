# -*- coding=utf-8
"""
perfomance_report module
"""
from django.db import models


class PerformanceReport(models.Model):
    """
    PerfomanceReport
    """
    sprayformid = models.CharField(max_length=20)
    found = models.IntegerField(default=0)
    sprayed = models.IntegerField(default=0)
    refused = models.IntegerField(default=0)
    other = models.IntegerField(default=0)
    spray_date = models.DateField(db_index=True)
    team_leader = models.ForeignKey('TeamLeader')
    team_leader_assistant = models.ForeignKey('TeamLeaderAssistant')
    spray_operator = models.ForeignKey('SprayOperator')
    start_time = models.TimeField()
    end_time = models.TimeField()
    data_quality_check = models.BooleanField()
    reported_found = models.IntegerField(default=0)
    reported_sprayed = models.IntegerField(default=0)
    not_eligible = models.IntegerField(default=0)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'main'
        unique_together = ('spray_operator', 'sprayformid')
