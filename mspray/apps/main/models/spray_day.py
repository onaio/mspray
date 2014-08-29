# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models
from jsonfield import JSONField

DATA_ID_FIELD = '_id'
DATE_FIELD = 'today'
STRUCTURE_GPS_FIELD = 'structure_gps'
NON_STRUCTURE_GPS_FIELD = 'non_structure_gps'


class SprayDay(models.Model):
    submission_id = models.PositiveIntegerField(unique=True)
    spray_date = models.DateField(db_index=True)
    geom = models.PointField(srid=4326)
    data = JSONField(default={})

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.spray_date.isoformat()

# Auto-generated `LayerMapping` dictionary for SprayDay model
sprayday_mapping = {
    'geom': 'POINT25D',
}
