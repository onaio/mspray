# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class Household(models.Model):
    hh_id = models.IntegerField()
    name = models.CharField(max_length=100)
    descr = models.CharField(max_length=254)
    folder = models.CharField(max_length=100)
    geom = models.MultiPointField(srid=4326)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.name


# Auto-generated `LayerMapping` dictionary for Household model
household_mapping = {
    'hh_id': 'Id',
    'name': 'NAME',
    'descr': 'DESCR',
    'folder': 'FOLDER',
    'geom': 'MULTIPOINT',
}
