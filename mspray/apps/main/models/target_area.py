# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class TargetArea(models.Model):
    houses = models.FloatField(db_index=True)
    targetid = models.FloatField()
    predicted = models.FloatField()
    predinc = models.FloatField()
    ranks = models.FloatField(db_index=True)
    houseranks = models.FloatField()
    targeted = models.FloatField(db_index=True)
    district_name = models.CharField(db_index=True, max_length=254)
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    TARGETED_VALUE = 1

    class Meta:
        app_label = 'main'

    def __str__(self):
        return '%s' % self.district_name


# Auto-generated `LayerMapping` dictionary for TargetArea model
targetarea_mapping = {
    'houses': 'Houses',
    'targetid': 'targetid',
    'predicted': 'predicted',
    'predinc': 'predinc',
    'ranks': 'ranks',
    'houseranks': 'houseranks',
    'targeted': 'targeted',
    'district_name': 'DISTRICTNA',
    'geom': 'MULTIPOLYGON',
}
