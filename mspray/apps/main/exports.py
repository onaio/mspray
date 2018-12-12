# -*- coding: utf-8 -*-
"""Export functions."""
import csv
from tempfile import TemporaryFile

from django.core.files.base import File
from django.core.files.storage import default_storage

from mspray.apps.main.models import Location
from mspray.apps.main.serializers.target_area import TargetAreaRichSerializer


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
