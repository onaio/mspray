# This is an auto-generated Django model module created by ogrinspect.
from django.conf import settings
from django.contrib.gis.db import models
from django_pgjson.fields import JsonField

DATA_FILTER = getattr(settings, 'MSPRAY_DATA_FILTER',
                      '"sprayable_structure":"yes"')
DATA_ID_FIELD = getattr(settings, 'MSPRAY_DATA_ID_FIELD', '_id')
DATE_FIELD = getattr(settings, 'MSPRAY_DATE_FIELD', 'today')
STRUCTURE_GPS_FIELD = getattr(settings, 'MSPRAY_STRUCTURE_GPS_FIELD',
                              'structure_gps')
NON_STRUCTURE_GPS_FIELD = getattr(settings, 'MSPRAY_NON_STRUCTURE_GPS_FIELD',
                                  'non_structure_gps')


class SprayDay(models.Model):
    submission_id = models.PositiveIntegerField(unique=True)
    spray_date = models.DateField(db_index=True)
    geom = models.PointField(srid=4326, db_index=True, null=True)
    bgeom = models.GeometryField(srid=4326, db_index=True, null=True)
    data = JsonField(default={})
    location = models.ForeignKey('Location', db_index=True, null=True)
    team_leader = models.ForeignKey('TeamLeader', db_index=True, null=True)
    spray_operator = models.ForeignKey('SprayOperator', db_index=True,
                                       null=True)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.spray_date.isoformat()

# Auto-generated `LayerMapping` dictionary for SprayDay model
sprayday_mapping = {
    'geom': 'POINT25D',
}
