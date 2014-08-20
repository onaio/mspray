# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class TargetArea(models.Model):
    objectid = models.IntegerField(db_index=True)
    houses = models.IntegerField(db_index=True)
    target_fid = models.IntegerField(null=True, blank=True)
    targetid = models.FloatField(db_index=True)
    predicted = models.FloatField()
    predinc = models.FloatField()
    ranks = models.FloatField()
    houseranks = models.FloatField()
    targeted = models.FloatField(db_index=True)
    district_name = models.CharField(max_length=254)
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    rank_house = models.CharField(db_index=True, max_length=50)
    geom = models.PolygonField(srid=4326)
    objects = models.GeoManager()

    TARGETED_VALUE = 1

    class Meta:
        app_label = 'main'

    def __str__(self):
        return '%s' % self.rank_house


# Auto-generated `LayerMapping` dictionary for TargetArea model

targetarea_mapping = {
    'objectid': 'OBJECTID',
    'houses': 'Join_Count',
    'target_fid': 'TARGET_FID',
    'targetid': 'targetid',
    'predicted': 'predicted',
    'predinc': 'predinc',
    'ranks': 'ranks',
    'houseranks': 'houseranks',
    'targeted': 'targeted',
    'district_name': 'DISTRICTNA',
    'shape_leng': 'Shape_Leng',
    'shape_area': 'Shape_Area',
    'rank_house': 'rank_house',
    'geom': 'POLYGON',
}
