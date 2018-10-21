# -*- coding:utf-8 -*-
"""
Decision model.
"""

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

from mspray.apps.main.models.location import Location
from mspray.libs.common_tags import DATA_ID_FIELD, SPRAY_AREA_FIELD


class Decision(models.Model):
    """
    Decision model.
    """

    submission_id = models.PositiveIntegerField(unique=True)
    today = models.DateField()
    geom = models.PointField(srid=4326, null=True)
    data = JSONField()
    household = models.ForeignKey(
        "Household",
        on_delete=models.SET_NULL,
        related_name="decision_households",
        null=True,
    )
    spray_area = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
        related_name="decision_spray_areas",
    )
    health_facility = models.ForeignKey(
        "Location",
        on_delete=models.CASCADE,
        related_name="decision_health_facilities",
    )
    district = models.ForeignKey(
        "Location", on_delete=models.CASCADE, related_name="decision_districts"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "main"


def create_decision_visit(data):
    """Creates a Decision record from a Spray Area Decision Form.
    """
    district = health_facility = spray_area = None
    submission_id = data.get(DATA_ID_FIELD)
    today = data.get("today")
    spray_area = data.get(SPRAY_AREA_FIELD)
    if spray_area:
        # get location by spray_area
        try:
            spray_area = Location.objects.get(name=spray_area, level="ta")
        except Location.DoesNotExist:
            spray_area = None
        else:
            district = spray_area.parent.parent
            health_facility = spray_area.parent

    return Decision.objects.create(
        data=data,
        submission_id=submission_id,
        district=district,
        health_facility=health_facility,
        spray_area=spray_area,
        today=today,
    )
