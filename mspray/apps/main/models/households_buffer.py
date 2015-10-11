# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class HouseholdsBuffer(models.Model):
    location = models.ForeignKey('Location')
    num_households = models.IntegerField(default=0)
    geom = models.PolygonField(srid=4326)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'
