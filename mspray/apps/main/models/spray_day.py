# -*- coding=utf-8
"""
SprayDay model module - holds all submissions for the IRS HH Form
"""
# This is an auto-generated Django model module created by ogrinspect.
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save, pre_save

DATA_FILTER = getattr(
    settings, "MSPRAY_DATA_FILTER", '"sprayable_structure":"yes"'
)
DATA_ID_FIELD = getattr(settings, "MSPRAY_DATA_ID_FIELD", "_id")
DATE_FIELD = getattr(settings, "MSPRAY_DATE_FIELD", "today")
STRUCTURE_GPS_FIELD = getattr(
    settings, "MSPRAY_STRUCTURE_GPS_FIELD", "structure_gps"
)
NON_STRUCTURE_GPS_FIELD = getattr(
    settings, "MSPRAY_NON_STRUCTURE_GPS_FIELD", "non_structure_gps"
)
WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
NEW_WAS_SPRAYED_FIELD = settings.MSPRAY_NEW_STRUCTURE_WAS_SPRAYED_FIELD
SPRAYABLE_FIELD = settings.SPRAYABLE_FIELD
NEW_STRUCTURE_SPRAYABLE_FIELD = settings.NEW_STRUCTURE_SPRAYABLE_FIELD
NOT_SPRAYABLE_VALUE = settings.NOT_SPRAYABLE_VALUE
SPRAYED_VALUE = getattr(settings, "MSPRAY_WAS_SPRAYED_VALUE", "yes")
OSM_STRUCTURE_FIELD = getattr(settings, "MSPRAY_UNIQUE_FIELD", None)
NEW_STRUCTURE_GPS_FIELD = getattr(
    settings, "NEW_STRUCTURE_GPS_FIELD", "newstructure/gps_osm_file"
)


def get_osmid(data):
    """
    Returns the OSM way id or node id depending on what is in the data.
    """
    if OSM_STRUCTURE_FIELD:
        return (
            data.get("%s:way:id" % OSM_STRUCTURE_FIELD)
            or data.get("%s:node:id" % OSM_STRUCTURE_FIELD)
            or data.get("%s:node:id" % NEW_STRUCTURE_GPS_FIELD)
        )

    return None


class SprayDay(models.Model):
    """
    SprayDay model  - IRS HH submission data model.
    """

    submission_id = models.PositiveIntegerField(unique=True)
    osmid = models.BigIntegerField(null=True, db_index=True)
    spray_date = models.DateField(db_index=True)
    geom = models.PointField(srid=4326, db_index=True, null=True)
    bgeom = models.GeometryField(srid=4326, db_index=True, null=True)
    data = JSONField(default=dict)
    location = models.ForeignKey(
        "Location", db_index=True, null=True, on_delete=models.CASCADE
    )
    rhc = models.ForeignKey(
        "Location",
        db_index=True,
        null=True,
        related_name="visited_rhc",
        on_delete=models.CASCADE,
    )
    district = models.ForeignKey(
        "Location",
        db_index=True,
        null=True,
        related_name="visited_district",
        on_delete=models.CASCADE,
    )
    team_leader = models.ForeignKey(
        "TeamLeader", db_index=True, null=True, on_delete=models.CASCADE
    )
    team_leader_assistant = models.ForeignKey(
        "TeamLeaderAssistant",
        db_index=True,
        null=True,
        on_delete=models.CASCADE,
    )
    spray_operator = models.ForeignKey(
        "SprayOperator", db_index=True, null=True, on_delete=models.CASCADE
    )
    household = models.ForeignKey(
        "Household", null=True, on_delete=models.SET_NULL
    )
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    was_sprayed = models.BooleanField(default=False)
    sprayable = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "main"

    def __str__(self):
        return self.spray_date.isoformat()

    def _set_sprayed_status(self):
        # pylint: disable=no-member
        was_sprayed_field = getattr(
            settings, "MSPRAY_WAS_SPRAYED_FIELD", WAS_SPRAYED_FIELD
        )
        sprayed_values = getattr(settings, "SPRAYED_VALUES", [])
        if self.data.get(was_sprayed_field):
            if sprayed_values:
                self.was_sprayed = (
                    self.data.get(was_sprayed_field) in sprayed_values
                )
            else:
                self.was_sprayed = (
                    self.data.get(was_sprayed_field) == SPRAYED_VALUE
                )
        elif self.data.get(NEW_WAS_SPRAYED_FIELD):
            self.was_sprayed = (
                self.data.get(NEW_WAS_SPRAYED_FIELD) == SPRAYED_VALUE
            )

    def _set_sprayable_status(self):
        # pylint: disable=no-member
        sprayable_field = getattr(settings, "SPRAYABLE_FIELD", SPRAYABLE_FIELD)
        new_sprayable_field = getattr(
            settings, "NEW_STRUCTURE_SPRAYABLE_FIELD", NEW_STRUCTURE_GPS_FIELD
        )
        not_sprayable_value = getattr(
            settings, "NOT_SPRAYABLE_VALUE", NOT_SPRAYABLE_VALUE
        )
        if self.data.get(sprayable_field):
            self.sprayable = (
                self.data.get(sprayable_field) != not_sprayable_value
            )
        elif self.data.get(new_sprayable_field):
            self.sprayable = (
                self.data.get(new_sprayable_field) != not_sprayable_value
            )

    def has_osm_data(self):
        """
        Check if OSM data has been received for this record
        we assume that if settings.MSPRAY_OSM_PRESENCE_FIELD is present
        then this record has received OSM data
        """
        return settings.MSPRAY_OSM_PRESENCE_FIELD in self.data

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        from mspray.apps.main.utils import get_formid  # noqa

        self._set_sprayed_status()
        self._set_sprayable_status()

        if "sprayformid" and self.spray_operator:
            self.data.update(
                {  # pylint: disable=no-member
                    "sprayformid": get_formid(
                        self.spray_operator, self.spray_date
                    )
                }
            )
        osmid = get_osmid(self.data)
        try:
            if osmid and int(osmid) != self.osmid and not self.location:
                self.osmid = osmid
        except ValueError:
            pass

        return super(SprayDay, self).save(*args, **kwargs)


class SprayDayHealthCenterLocation(models.Model):
    """
    SprayDayHealthCenterLocation model - direct link between a SprayDay
    submission to a Health Facility location.
    """

    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    content_object = models.ForeignKey("SprayDay", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("location", "content_object")


# pylint: disable=unused-argument
def link_health_center_location(sender, instance=None, **kwargs):
    """
    Link a submission to a Health Facility.
    """
    if instance and instance.location:
        SprayDayHealthCenterLocation.objects.get_or_create(
            location=instance.location.parent, content_object=instance
        )


post_save.connect(
    link_health_center_location,
    sender=SprayDay,
    dispatch_uid="link_health_center_location",
)


class SprayDayDistrict(models.Model):
    """
    SprayDayDistrict model - direct linke between a SprayDay submission to a
    District location.
    """

    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    content_object = models.ForeignKey("SprayDay", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("location", "content_object")


def link_district_location(sender, instance=None, **kwargs):
    """
    Link a submission to a district location.
    """
    if instance and instance.location:
        SprayDayDistrict.objects.get_or_create(
            location=instance.location.parent,
            content_object=instance.content_object,
        )


post_save.connect(
    link_district_location,
    sender=SprayDayHealthCenterLocation,
    dispatch_uid="link_district_location",
)


def mda_population_calculations(sender, instance=None, **kwargs):
    """Calculate MDA population metrics"""
    eligible_field = "_population_eligible"
    treatment_field = "_population_treatment"
    persons_field = "sprayable/anotherperson"
    if instance.data and eligible_field not in instance.data:
        instance.data[eligible_field] = 0
        instance.data[treatment_field] = 0
        if persons_field in instance.data:
            for person in instance.data[persons_field]:
                if person.get("{}/eligible".format(persons_field)) == "yes":
                    instance.data[eligible_field] += 1
                    treatment = person.get(
                        "{}/treatment".format(persons_field)
                    )
                    if treatment == "received":
                        instance.data[treatment_field] += 1


pre_save.connect(
    mda_population_calculations,
    sender=SprayDay,
    dispatch_uid="mda_population_calculations",
)
# Auto-generated `LayerMapping` dictionary for SprayDay model
sprayday_mapping = {"geom": "POINT25D"}  # pylint: disable=C0103
