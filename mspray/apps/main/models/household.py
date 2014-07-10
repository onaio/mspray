# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class Household(models.Model):
    hh_id = models.IntegerField()
    hh_type = models.CharField(max_length=1)
    comment = models.CharField(max_length=60)
    type_1 = models.CharField(max_length=1)
    comment_1 = models.CharField(max_length=60)
    name = models.CharField(max_length=254)
    descr = models.CharField(max_length=254)
    orig_fid = models.IntegerField()
    geom = models.MultiPointField(srid=4326)
    bgeom = models.PolygonField(srid=4326, null=True, blank=True)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.name

# Auto-generated `LayerMapping` dictionary for Household model
household_mapping = {
    'hh_id': 'id',
    'hh_type': 'type',
    'comment': 'comment',
    'type_1': 'Type_1',
    'comment_1': 'Comment_1',
    'name': 'Name',
    'descr': 'Descriptio',
    'orig_fid': 'ORIG_FID',
    'geom': 'MULTIPOINT',
}
