# -*- coding=utf-8 -*-
"""
Load TeamLeaders from a CSV file.
"""
import codecs
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location, TeamLeader


class Command(BaseCommand):
    """
    Load TeamLeaders from a CSV file command.
    """

    args = "<path to team leaders csv with columns code|name>"
    help = _("Load team leaders")

    def add_arguments(self, parser):
        parser.add_argument("csv_file", metavar="FILE")

    def handle(self, *args, **options):
        if "csv_file" not in options:
            raise CommandError(_("Missing team leaders csv file path"))
        else:
            try:
                path = os.path.abspath(options["csv_file"])
            except FileNotFoundError as error:
                raise CommandError(_("Error: %(msg)s" % {"msg": error}))
            else:
                with codecs.open(path, encoding="utf-8") as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    codes = []
                    for row in csv_reader:
                        try:
                            leader, created = TeamLeader.objects.get_or_create(
                                code=row["code"].strip(), name=row["name"]
                            )
                        except IntegrityError:
                            leader = TeamLeader.objects.get(code=row["code"])
                            leader.name = row["name"].strip()
                            leader.save()
                        else:
                            if created:
                                print(row)
                        codes.append(row["code"])
                        district = row["district"].strip()
                        if district:
                            location = Location.get_district_by_code_or_name(
                                district
                            )
                            leader.location = location
                            leader.save()
                    print(TeamLeader.objects.exclude(code__in=codes).delete())
