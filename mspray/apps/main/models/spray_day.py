# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models
from jsonfield import JSONField


class SprayDay(models.Model):
    spray_date = models.DateField()
    geom = models.PointField(srid=4326)
    data = JSONField(default={})

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.date.isoformat()

# Auto-generated `LayerMapping` dictionary for SprayDay model
sprayday_mapping = {
    'geom': 'POINT25D',
}
