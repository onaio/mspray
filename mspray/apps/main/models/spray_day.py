# This is an auto-generated Django model module created by ogrinspect.
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save

DATA_FILTER = getattr(settings, 'MSPRAY_DATA_FILTER',
                      '"sprayable_structure":"yes"')
DATA_ID_FIELD = getattr(settings, 'MSPRAY_DATA_ID_FIELD', '_id')
DATE_FIELD = getattr(settings, 'MSPRAY_DATE_FIELD', 'today')
STRUCTURE_GPS_FIELD = getattr(settings, 'MSPRAY_STRUCTURE_GPS_FIELD',
                              'structure_gps')
NON_STRUCTURE_GPS_FIELD = getattr(settings, 'MSPRAY_NON_STRUCTURE_GPS_FIELD',
                                  'non_structure_gps')
WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
WAS_SPRAYED_VALUE = getattr(settings, 'MSPRAY_WAS_SPRAYED_VALUE', 'yes')
OSM_STRUCTURE_FIELD = getattr(settings, 'MSPRAY_UNIQUE_FIELD', None)


def get_osmid(data):
    if OSM_STRUCTURE_FIELD:
        return data.get('%s:way:id' % OSM_STRUCTURE_FIELD) \
            or data.get('%s:node:id' % OSM_STRUCTURE_FIELD)


class SprayDay(models.Model):
    submission_id = models.PositiveIntegerField(unique=True)
    osmid = models.BigIntegerField(null=True, db_index=True)
    spray_date = models.DateField(db_index=True)
    geom = models.PointField(srid=4326, db_index=True, null=True)
    bgeom = models.GeometryField(srid=4326, db_index=True, null=True)
    data = JSONField(default={})
    location = models.ForeignKey('Location', db_index=True, null=True)
    rhc = models.ForeignKey('Location', db_index=True, null=True,
                            related_name='visited_rhc')
    district = models.ForeignKey('Location', db_index=True, null=True,
                                 related_name='visited_district')
    team_leader = models.ForeignKey('TeamLeader', db_index=True, null=True)
    team_leader_assistant = models.ForeignKey(
        'TeamLeaderAssistant', db_index=True, null=True
    )
    spray_operator = models.ForeignKey('SprayOperator', db_index=True,
                                       null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    was_sprayed = models.BooleanField(default=False)

    objects = models.GeoManager()

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.spray_date.isoformat()

    def save(self, *args, **kwargs):
        from mspray.apps.main.utils import get_formid  # noqa

        data = self.data

        was_sprayed = data.get(WAS_SPRAYED_FIELD)
        if was_sprayed == WAS_SPRAYED_VALUE:
            self.was_sprayed = True

        if 'sprayformid' and self.spray_operator:
            self.data['sprayformid'] = get_formid(self.spray_operator,
                                                  self.spray_date)
        osmid = get_osmid(self.data)
        try:
            if osmid and int(osmid) != self.osmid:
                self.osmid = osmid
        except:
            pass

        return super(SprayDay, self).save(*args, **kwargs)


class SprayDayHealthCenterLocation(models.Model):
    location = models.ForeignKey('Location')
    content_object = models.ForeignKey('SprayDay')

    class Meta:
        unique_together = ('location', 'content_object')


def link_health_center_location(sender, instance=None, **kwargs):
    if instance and instance.location:
        SprayDayHealthCenterLocation.objects.get_or_create(
            location=instance.location.parent,
            content_object=instance
        )

post_save.connect(link_health_center_location, sender=SprayDay,
                  dispatch_uid='link_health_center_location')


class SprayDayDistrict(models.Model):
    location = models.ForeignKey('Location')
    content_object = models.ForeignKey('SprayDay')

    class Meta:
        unique_together = ('location', 'content_object')


def link_district_location(sender, instance=None, **kwargs):
    if instance and instance.location:
        SprayDayDistrict.objects.get_or_create(
            location=instance.location.parent,
            content_object=instance.content_object
        )

post_save.connect(link_district_location, sender=SprayDayHealthCenterLocation,
                  dispatch_uid='link_district_location')

# Auto-generated `LayerMapping` dictionary for SprayDay model
sprayday_mapping = {
    'geom': 'POINT25D',
}
