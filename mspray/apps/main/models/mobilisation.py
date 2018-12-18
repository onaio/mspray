# -*- coding:utf-8 -*-
"""Mobilisation model."""

import logging
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models.signals import post_save

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.location import Location

from mspray.libs.common_tags import (
    DATA_ID_FIELD,
    MOBILISATION_OSM_FIELD,
    MOBILISED_FIELD,
    SPRAY_AREA_FIELD,
    MOBILISATION_LATITUDE_FIELD,
    MOBILISATION_LONGITUDE_FIELD,
)

OSM_ID_FIELD = "{}:way:id".format(MOBILISATION_OSM_FIELD)
logger = logging.getLogger(__name__)


class Mobilisation(models.Model):
    """Mobilisation model."""

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
        """Mobilisation model."""

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
    district = health_facility = household = spray_area = None
    is_mobilised = data.get(MOBILISED_FIELD) in ["Yes", "paper"]
    submission_id = data.get(DATA_ID_FIELD)
    osmid = data.get(OSM_ID_FIELD)
    # Get spray area by osmid
    if osmid:
        try:
            household = Household.objects.get(hh_id=osmid)
        except Household.DoesNotExist:
            pass

    if household:
        spray_area = household.location
    # Get spray are by GPS
    if not household:
        # link mobilisation using geo spatial query
        lon = data.get(MOBILISATION_LONGITUDE_FIELD)
        lat = data.get(MOBILISATION_LATITUDE_FIELD)
        if lat is not None and lon is not None:
            geom = Point(lon, lat)
            # check if the geom contains Point
            # if yes, save that as the spray area
            if geom is not None:
                locations = Location.objects.filter(
                    geom__contains=geom,
                    level=settings.MSPRAY_TA_LEVEL)
                if locations:
                    spray_area = locations[0]
                else:
                    logger.info(
                        "No GPS data found for {}".format(
                            submission_id))
    # get location by spray_area
    if not spray_area:
        spray_area = data.get(SPRAY_AREA_FIELD)
        try:
            spray_area = Location.objects.get(
                name=spray_area, level="ta")
        except Location.DoesNotExist:
            logger.info("No spray area found for {}".format(
                submission_id))

    if spray_area:
        health_facility = spray_area.parent
        district = spray_area.parent.parent

    return Mobilisation.objects.create(
        data=data,
        submission_id=submission_id,
        is_mobilised=is_mobilised,
        district=district,
        health_facility=health_facility,
        spray_area=spray_area,
        household=household,
    )
