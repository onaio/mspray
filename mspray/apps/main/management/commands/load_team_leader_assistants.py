# -*- coding=utf-8 -*-
"""
Load TeamLeaderAssistant from a CSV File.
"""
import codecs
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location, TeamLeader, TeamLeaderAssistant


class Command(BaseCommand):
    """
    Load TeamLeaderAssistant from a CSV File.
    """

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
                            team_leader_assistant, created = TeamLeaderAssistant.objects.get_or_create(  # noqa pylint: disable=line-too-long
                                code=row["code"].strip(), name=row["name"]
                            )
                        except IntegrityError:
                            team_leader_assistant = TeamLeaderAssistant.objects.get(  # noqa pylint: disable=line-too-long
                                code=row["code"]
                            )
                            team_leader_assistant.name = row["name"]
                            team_leader_assistant.save()
                        else:
                            if created:
                                print(row)
                        codes.append(row["code"])
                        if row.get("health_facility_code"):
                            try:
                                team_leader_assistant.location = Location.objects.get(  # noqa pylint: disable=line-too-long
                                    code=row.get(
                                        "health_facility_code"
                                    ).strip(),
                                    level="RHC",
                                ).parent
                            except Location.DoesNotExist:
                                pass
                            else:
                                team_leader_assistant.save()

                        if row.get("district"):
                            team_leader_assistant.location = Location.get_district_by_code_or_name(  # noqa pylint: disable=line-too-long
                                row.get("district").strip()
                            )
                            team_leader_assistant.save()
                        if row.get("team_leader"):
                            team_leader_assistant.team_leader = TeamLeader.objects.get(  # noqa pylint: disable=line-too-long
                                code=row.get("team_leader").strip()
                            )

                            team_leader_assistant.save()
                    print(
                        TeamLeaderAssistant.objects.exclude(
                            code__in=codes
                        ).delete()
                    )
