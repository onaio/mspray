# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class TargetArea(models.Model):
    targetid = models.IntegerField()
    district_name = models.CharField(max_length=254)
    houses = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

targetarea_mapping = {
    'targetid': 'UniqueID_1',
    'district_name': 'HDist_1',
    'houses': 'Count_12',
    'geom': 'MULTIPOLYGON',
}
