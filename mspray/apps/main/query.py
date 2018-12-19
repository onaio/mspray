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
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from mspray.apps.main.models import Location
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
                Q(content_object__data__has_key="osmstructure:node:id")
                | Q(**new_gps)
                | Q(
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
                Q(
                    content_object__sprayable=True,
                    content_object__spraypoint__isnull=False,
                )
                | Q(
                    content_object__sprayable=True,
                    content_object__spraypoint__isnull=True,
                    content_object__was_sprayed=True,
                )
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
                Q(data__has_key="osmstructure:node:id")
                | Q(data__has_key="newstructure/gps_osm_file:node:id")
                | Q(
                    data__has_key="osmstructure:way:id", household__isnull=True
                ),
                location=OuterRef("pk"),
            )
            .order_by()
            .values("location")
        )
        new_structure_count = (
            sprays.filter(
                Q(sprayable=True, spraypoint__isnull=False)
                | Q(sprayable=True, spraypoint__isnull=True, was_sprayed=True)
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


def debug_spray_area_indicators(spray_area_id):
    """Print spray area indicators for debugging purposes."""
    location = Location.objects.get(pk=spray_area_id, level="ta")
    print(location)

    unique_points = list(
        location.spraypoint_set.values_list("sprayday", flat=True)
    )
    print("Unique Points:", len(unique_points))

    print("Households Sprayable")
    print(location.household_set.exclude(sprayable=False).count())

    print("New Structures")
    print(
        location.sprayday_set.filter(
            id__in=unique_points, sprayable=True, household__isnull=True
        ).count()
    )
    print(
        location.sprayday_set.exclude(id__in=unique_points)
        .filter(sprayable=True, household__isnull=True)
        .count()
    )
    print(
        location.sprayday_set.exclude(id__in=unique_points)
        .filter(sprayable=True, household__isnull=True, was_sprayed=True)
        .count()
    )

    print("# Total Sprayable")
    print(location.sprayday_set.filter(sprayable=True).count())

    print("# Total Sprayable Unique Set")
    print(
        location.sprayday_set.filter(
            sprayable=True, id__in=unique_points
        ).count()
    )

    print("# Total Sprayed")
    print(location.sprayday_set.filter(was_sprayed=True).count())

    print("# Total Sprayed Not in Unique Set")
    print(
        location.sprayday_set.filter(sprayable=True, was_sprayed=True)
        .exclude(id__in=unique_points)
        .count()
    )

    print("# Total Sprayable Sprayed")
    print(
        location.sprayday_set.filter(sprayable=True, was_sprayed=True).count()
    )

    print("# Total Sprayable Not Sprayed")
    print(
        location.sprayday_set.filter(sprayable=True, was_sprayed=False).count()
    )

    queryset = location.sprayday_set.filter(
        sprayable=True, was_sprayed=False, id__in=unique_points
    )
    print("# Total Sprayable Unique Set Not Sprayed")
    print(queryset.count())
    print(queryset.values_list("id", flat=True))

    print("Sprayed duplicates")
    print(
        location.sprayday_queryset.filter(was_sprayed=True)
        .exclude(household__isnull=True)
        .values("household")
        .distinct()
        .annotate(duplicates=Count("household") - 1)
        .aggregate(total_duplicates=Sum("duplicates"))["total_duplicates"]
    )

    print("Not Sprayed duplicates")
    print(
        location.sprayday_set.filter(sprayable=True, was_sprayed=False)
        .exclude(id__in=unique_points)
        .count()
    )


def debug_submission_lists(list_one, list_two):
    """Print debug information from mspray submissions.

    arguments:
        list_one - primary keys of mspray submissions
        list_two - primary keys of mspray submissions
    """
    print(
        "Sprayable, Was Sprayed, data id, osmid, household, in l2, "
        "submissions with same osm, same osm and was sprayed, unique records"
    )
    for data_id in list_one:
        submission = SprayDay.objects.get(pk=data_id)
        print(
            submission.sprayable,
            submission.was_sprayed,
            submission.pk,
            submission.osmid,
            submission.household,
            data_id in list_two,
            SprayDay.objects.filter(osmid=submission.osmid).count(),
            SprayDay.objects.filter(
                osmid=submission.osmid, was_sprayed=True
            ).count(),
            submission.spraypoint_set.count(),
        )
