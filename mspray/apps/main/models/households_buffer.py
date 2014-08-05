# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models

from mspray.apps.main.models.target_area import TargetArea


class HouseholdsBuffer(models.Model):
    target_area = models.ForeignKey(TargetArea)
    geom = models.PolygonField(srid=4326)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'
