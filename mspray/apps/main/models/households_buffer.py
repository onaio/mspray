# -*- coding: utf-8 -*-
"""
HouseholdsBuffer model.
"""
# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class HouseholdsBuffer(models.Model):
    """
    HouseholdsBuffer model
    """

    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    num_households = models.IntegerField(default=0)
    geom = models.PolygonField(srid=4326)

    class Meta:
        app_label = "main"
