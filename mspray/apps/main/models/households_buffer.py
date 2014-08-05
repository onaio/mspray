# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class HouseholdsBuffer(models.Model):
    geom = models.PolygonField(srid=4326)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'
