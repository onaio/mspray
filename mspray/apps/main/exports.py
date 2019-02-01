# -*- coding: utf-8 -*-
"""Export functions."""
import csv
from tempfile import TemporaryFile

from django.core.files.base import File
from django.core.files.storage import default_storage

from mspray.apps.main.models import Location, SprayDay
from mspray.apps.main.views.sprayday import get_not_targeted_within_geom
from mspray.apps.main.serializers.target_area import (
    RichQuerysetMixin,
    SprayOperatorDailySummaryMixin,
    TargetAreaRichSerializer,
)


def detailed_spray_area_data(queryset=None):
    """Return detailed spray area data."""
    if queryset is None:
        queryset = Location.objects.filter(level="ta", target=True).order_by(
            "name"
        )

    yield [
        "Target Area",
        "District",
        "Structures Found",
        "Sprayed Structures",
        "Sprayed Total Pop",
        "Sprayed Males",
        "Sprayed Females",
        "Sprayed Pregnant Women",
        "Sprayed Children",
        "Not Sprayed Structures",
        "Not Sprayed Total Pop",
        "Not Sprayed Males",
        "Not Sprayed Females",
        "Not Sprayed Pregnant Women",
        "Not Sprayed Children",
        "Rooms Found",
        "Rooms Sprayed ",
        "Nets Total Available",
        "Nets People Covered",
        "Bottles Issued",
        "Bottles Full",
        "Bottles Empty",
        "Bottles Not Returned",
    ]
    for spray_area in queryset.iterator():
        item = TargetAreaRichSerializer(spray_area).data
        yield [
            item["name"],
            item["district"],
            item["found"],
            item["visited_sprayed"],
            item["sprayed_totalpop"],
            item["sprayed_males"],
            item["sprayed_females"],
            item["sprayed_pregwomen"],
            item["sprayed_childrenU5"],
            item["visited_not_sprayed"],
            item["unsprayed_totalpop"],
            item["unsprayed_males"],
            item["unsprayed_females"],
            item["unsprayed_pregnant_women"],
            item["unsprayed_children_u5"],
            item["total_rooms"],
            item["sprayed_rooms"],
            item["total_nets"],
            item["total_uNet"],
            item["bottles_start"],
            item["bottles_full"],
            item["bottles_empty"],
            item["bottles_accounted"],
        ]


def detailed_spray_area_to_file(filename="detailed_sprayareas.csv"):
    """Write the detailed spray area report to file."""
    with TemporaryFile(mode="w+", encoding="utf-8") as file_pointer:
        spray_areas_file = File(file_pointer)
        writer = csv.writer(spray_areas_file)
        for row in detailed_spray_area_data():
            writer.writerow(row)
        if default_storage.exists(filename):
            default_storage.delete(filename)
        spray_areas_file.seek(0)
        default_storage.save(filename, spray_areas_file)


def get_not_targeted_data(rhc: object):
    """
    Returns data for spray events not tied to a target area

    :param rhc: the RHC location object
    :return: dict of data
    """
    sprays = SprayDay.objects.filter(location=None, geom__within=rhc.geom)

    spray_metrics = get_not_targeted_within_geom(rhc.geom)[0]

    sop = SprayOperatorDailySummaryMixin()
    sop.queryset = sprays

    rich_data = RichQuerysetMixin()
    rich_data.queryset = sprays

    return {
        "name": "Not in Target Area",
        "rhc": rhc.name,
        "district": rhc.parent.name,
        "found": spray_metrics["found"],
        "visited_sprayed": spray_metrics["sprayed"],
        "visited_not_sprayed": spray_metrics["not_sprayed"],
        "sprayed_totalpop": rich_data.get_sprayed_totalpop(),
        "sprayed_males": rich_data.get_sprayed_males(),
        "sprayed_females": rich_data.get_sprayed_females(),
        "sprayed_pregwomen": rich_data.get_sprayed_pregwomen(),
        "sprayed_childrenU5": rich_data.get_sprayed_childrenU5(),
        "unsprayed_totalpop": rich_data.get_unsprayed_totalpop(),
        "unsprayed_males": rich_data.get_unsprayed_males(),
        "unsprayed_females": rich_data.get_unsprayed_females(),
        "unsprayed_pregnant_women": rich_data.get_unsprayed_pregnant_women(),
        "unsprayed_children_u5": rich_data.get_unsprayed_children_u5(),
        "total_rooms": rich_data.get_total_rooms(),
        "sprayed_rooms": rich_data.get_sprayed_rooms(),
        "total_nets": rich_data.get_total_nets(),
        "total_uNet": rich_data.get_total_uNet(),
        "bottles_start": sop.get_bottles_start(),
        "bottles_full": sop.get_bottles_full(),
        "bottles_empty": sop.get_bottles_empty(),
        "bottles_accounted": sop.get_bottles_accounted(),
    }
