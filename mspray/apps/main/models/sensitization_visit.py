# -*- coding:utf-8 -*-
"""
SensitizationVisit model.
"""

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save

from mspray.apps.main.models.household import Household
from mspray.libs.common_tags import (
    DATA_ID_FIELD,
    SENSITIZATION_OSM_FIELD,
    SENSITIZED_FIELD,
)

OSM_ID_FIELD = "{}:way:id".format(SENSITIZATION_OSM_FIELD)


class SensitizationVisit(models.Model):
    """
    SensitizationVisit model.
    """

    submission_id = models.PositiveIntegerField(unique=True)
    geom = models.PointField(srid=4326, null=True)
    data = JSONField()
    is_sensitized = models.BooleanField()
    household = models.ForeignKey(
        "Household",
        on_delete=models.SET_NULL,
        related_name="sv_households",
        null=True,
    )
    spray_area = models.ForeignKey(
        "Location", on_delete=models.CASCADE, related_name="sv_spray_areas"
    )
    health_facility = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
        related_name="sv_health_facilities",
    )
    district = models.ForeignKey(
        "Location", on_delete=models.CASCADE, related_name="sv_districts"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "main"


def update_location_sensitization(sender, instance=None, **kwargs):
    """Update is_sensitized value on location objects"""
    if kwargs.get("created") and instance and sender == SensitizationVisit:
        instance.spray_area.is_sensitized = instance.is_sensitized
        instance.spray_area.save()


post_save.connect(
    update_location_sensitization,
    sender=SensitizationVisit,
    dispatch_uid="update_location_sensitization_visit",
)


def create_sensitization_visit(data):
    """Creates a SensitizationVisit object from a Sensitization Visit form.
    """
    district = health_facility = household = spray_area = None
    is_sensitized = data.get(SENSITIZED_FIELD) in ["Yes"]
    submission_id = data.get(DATA_ID_FIELD)
    osmid = data.get(OSM_ID_FIELD)
    try:
        household = Household.objects.get(hh_id=osmid)
    except Household.DoesNotExist:
        pass

    if household:
        district = household.location.parent.parent
        health_facility = household.location.parent
        spray_area = household.location

    return SensitizationVisit.objects.create(
        data=data,
        submission_id=submission_id,
        is_sensitized=is_sensitized,
        district=district,
        health_facility=health_facility,
        spray_area=spray_area,
        household=household,
    )
