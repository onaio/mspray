# -*- coding=utf-8 -*-
"""
Weekly report model module.
"""
from django.db import models


class WeeklyReport(models.Model):
    """
    Weekly report model
    """
    week_number = models.PositiveIntegerField()
    location = models.ForeignKey('Location')
    # visited - 20% of the structures have been sprayed in the spray area
    visited = models.PositiveIntegerField(default=0)
    # sprayed - 20% of the structures have been sprayed in the spray area
    sprayed = models.PositiveIntegerField(default=0)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'main'
        unique_together = ('week_number', 'location')
