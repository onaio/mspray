# -*- coding=utf-8 -*-
"""
PerformanceReport model
"""
from django.contrib.postgres.fields import JSONField
from django.db import models


class PerformanceReport(models.Model):
    """
    PerformanceReport
    """

    sprayformid = models.CharField(max_length=20)
    found = models.IntegerField(default=0)
    sprayed = models.IntegerField(default=0)
    refused = models.IntegerField(default=0)
    other = models.IntegerField(default=0)
    spray_date = models.DateField(db_index=True)
    team_leader = models.ForeignKey(
        "TeamLeader", null=True, on_delete=models.CASCADE
    )
    team_leader_assistant = models.ForeignKey(
        "TeamLeaderAssistant", null=True, on_delete=models.CASCADE
    )
    spray_operator = models.ForeignKey(
        "SprayOperator", on_delete=models.CASCADE
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    data_quality_check = models.BooleanField(null=True)
    reported_found = models.IntegerField(default=0)
    reported_sprayed = models.IntegerField(default=0)
    not_eligible = models.IntegerField(default=0)
    district = models.ForeignKey("Location", on_delete=models.CASCADE)
    data = JSONField(default=dict)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "main"
        unique_together = ("spray_operator", "sprayformid")
