# -*- coding=utf-8 -*-
"""
load_location_shapefile command - loads districts, health facility catchment
area and spray area shapefiles.
"""
import os
import csv
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    """
    Uploads location information
    """

    help = _("Load locations")

    def add_arguments(self, parser):
        parser.add_argument("csv_file", metavar="FILE")
        parser.add_argument("level")

    def handle(self, *args, **options):  # pylint: disable=R0912,R0914,R0915
        if "csv_file" not in options:
            raise CommandError(_("Missing locations CSV file path"))
        else:
            try:
                path = os.path.abspath(options["csv_file"])
            except Exception as error:
                raise CommandError(_("Error: %(msg)s" % {"msg": error}))
            else:
                level = options["level"]
                names = Location.objects.filter(level=level).values_list(
                    "name", flat=True
                )
                actual_list = []
                with open(path) as csv_file:
                    csv_reader = csv.reader(csv_file)
                    for row in csv_reader:
                        if csv_reader.line_num == 1:
                            continue
                        if level == "district":
                            name = row[0]
                            code = int(row[1])
                            location = Location.objects.get(
                                name=name, level=level
                            )
                            if code != location.code:
                                location.code = code
                                location.save()
                            actual_list.append(name)
                        else:
                            name = row[0]
                            code = int(row[1])
                            parent_code = int(row[2])
                            location = Location.objects.get(
                                name=name, level=level
                            )
                            if code != location.code:
                                location.code = code
                                try:
                                    location.save()
                                except Exception:
                                    location.code = code * 9000
                                    location.save()
                                    print(row)
                            if parent_code != location.parent.code:
                                parent = Location.objects.get(
                                    code=parent_code, level="district"
                                )
                                location.parent = parent
                                try:
                                    location.save()
                                except Exception:
                                    print(row)
                            actual_list.append(name)
                    remove_list = set(names).difference(set(actual_list))
                    Location.objects.filter(
                        name__in=list(remove_list)
                    ).exclude(parent__code=99).delete()
                    print(remove_list)
