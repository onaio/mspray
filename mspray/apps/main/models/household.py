# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class Household(models.Model):
    hh_id = models.IntegerField(unique=True)
    geom = models.PointField(srid=4326)
    bgeom = models.PolygonField(srid=4326, null=True, blank=True)
    location = models.ForeignKey('Location', default=1)
    data = JSONField(default={})

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return str(self.hh_id)

# Auto-generated `LayerMapping` dictionary for Household model
household_mapping = {
    'hh_id': 'OBJECTID',
    'geom': 'POINT',
}
