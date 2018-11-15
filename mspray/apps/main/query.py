# -*- coding: utf-8 -*-
"""Query utils functions module."""

from django.db.models import (
    Count,
    ExpressionWrapper,
    F,
    IntegerField,
    OuterRef,
    PositiveIntegerField,
    Q,
    Subquery,
    Value,
)
from django.db.models.functions import Coalesce

from mspray.apps.main.models.spray_day import (
    SprayDay,
    SprayDayHealthCenterLocation,
)


def get_location_qs(queryset, level=None):
    """Return a Location queryset with aggreagates.

    Has the aggregates num_new_structures and
    total_structures calculations for each location.
    """
    if level == "RHC":
        new_gps = {
            "content_object__data__has_key": (
                "newstructure/gps_osm_file:node:id"
            )
        }
        sprays = (
            SprayDayHealthCenterLocation.objects.filter(
                Q(content_object__data__has_key="osmstructure:node:id") |
                Q(**new_gps) |
                Q(
                    content_object__data__has_key="osmstructure:way:id",
                    content_object__household__isnull=True,
                ),
                location=OuterRef("pk"),
            )
            .order_by()
            .values("location")
        )
        new_structure_count = (
            sprays.filter(
                Q(content_object__sprayable=True,
                    content_object__spraypoint__isnull=False) |
                Q(
                    content_object__sprayable=True,
                    content_object__spraypoint__isnull=True,
                    content_object__was_sprayed=True)
            )
            .annotate(c=Count("location"))
            .values("c")
        )
        queryset = queryset.annotate(
            num_new_structures=Coalesce(
                Subquery(
                    queryset=new_structure_count, output_field=IntegerField()
                ),
                Value(0),
            )
        ).annotate(
            total_structures=ExpressionWrapper(
                F("num_new_structures") + F("structures"),
                output_field=IntegerField(),
            )
        )
    else:
        sprays = (
            SprayDay.objects.filter(
                Q(data__has_key="osmstructure:node:id") |
                Q(data__has_key="newstructure/gps_osm_file:node:id") |
                Q(
                    data__has_key="osmstructure:way:id", household__isnull=True
                ),
                location=OuterRef("pk"),
            )
            .order_by()
            .values("location")
        )
        new_structure_count = (
            sprays.filter(
                Q(sprayable=True, spraypoint__isnull=False) |
                Q(sprayable=True, spraypoint__isnull=True, was_sprayed=True)
            )
            .annotate(c=Count("location"))
            .values("c")
        )
        queryset = queryset.annotate(
            num_new_structures=Coalesce(
                Subquery(
                    queryset=new_structure_count,
                    output_field=PositiveIntegerField(),
                ),
                Value(0),
            )
        ).annotate(
            total_structures=ExpressionWrapper(
                F("num_new_structures") + F("structures"),
                output_field=PositiveIntegerField(),
            )
        )

    return queryset
