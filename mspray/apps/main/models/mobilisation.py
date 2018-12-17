# -*- coding:utf-8 -*-
"""
Mobilisation model.
"""

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.db.models.signals import post_save

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.location import Location
from mspray.apps.main.models.spray_day import (
    NON_STRUCTURE_GPS_FIELD, STRUCTURE_GPS_FIELD)
from mspray.libs.common_tags import (
    DATA_ID_FIELD,
    MOBILISATION_OSM_FIELD,
    MOBILISED_FIELD,
    SPRAY_AREA_FIELD,
)

OSM_ID_FIELD = "{}:way:id".format(MOBILISATION_OSM_FIELD)


class Mobilisation(models.Model):
    """
    Mobilisation model.
    """

    submission_id = models.PositiveIntegerField(unique=True)
    geom = models.PointField(srid=4326, null=True)
    data = JSONField()
    is_mobilised = models.BooleanField()
    household = models.ForeignKey(
        "Household",
        on_delete=models.SET_NULL,
        related_name="mb_households",
        null=True,
    )
    spray_area = models.ForeignKey(
        "Location", on_delete=models.CASCADE, related_name="mb_spray_areas"
    )
    health_facility = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
        related_name="mb_health_facilities",
    )
    district = models.ForeignKey(
        "Location", on_delete=models.CASCADE, related_name="mb_districts"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "main"


def update_location_mobilisation(sender, instance=None, **kwargs):
    """Update is_mobilised value on location objects."""
    if kwargs.get("created") and instance and sender == Mobilisation:
        instance.spray_area.is_mobilised = instance.is_mobilised
        instance.spray_area.save()


post_save.connect(
    update_location_mobilisation,
    sender=Mobilisation,
    dispatch_uid="update_location_mobilisation_visit",
)


def create_mobilisation_visit(data):
    """Create a Mobilisation object from a Mobilisation Visit form."""
    from mspray.apps.main.utils import geojson_from_gps_string

    district = health_facility = household = spray_area = None
    is_mobilised = data.get(MOBILISED_FIELD) in ["Yes", "paper"]
    submission_id = data.get(DATA_ID_FIELD)
    osmid = data.get(OSM_ID_FIELD)
    if osmid:
        try:
            household = Household.objects.get(hh_id=osmid)
        except Household.DoesNotExist:
            pass

    if household:
        district = household.location.parent.parent
        health_facility = household.location.parent
        spray_area = household.location
    else:
        spray_area = data.get(SPRAY_AREA_FIELD)
        if spray_area:
            # get location by spray_area
            try:
                spray_area = Location.objects.get(name=spray_area, level="ta")
            except Location.DoesNotExist:
                pass
                # get the gps field

        gps_field = data.get(
            STRUCTURE_GPS_FIELD, data.get(NON_STRUCTURE_GPS_FIELD))
        geom = (geojson_from_gps_string(gps_field)
                if gps_field is not None else None)
        # check if the geom contains Point
        # if yes, save that as the spray area
        if geom is not None:
            locations = Location.objects.filter(
                geom__contains=geom,
                level=settings.MSPRAY_TA_LEVEL)
            if locations:
                spray_area = locations[0]
            else:
                district = spray_area.parent.parent
                health_facility = spray_area.parent

    return Mobilisation.objects.create(
        data=data,
        submission_id=submission_id,
        is_mobilised=is_mobilised,
        district=district,
        health_facility=health_facility,
        spray_area=spray_area,
        household=household,
    )
