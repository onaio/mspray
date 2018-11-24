# -*- coding=utf-8 -*-
"""
Load SprayOperators from a CSV file.
"""
import codecs
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.utils.translation import gettext as _

from mspray.apps.main.models import (
    Location,
    SprayOperator,
    TeamLeader,
    TeamLeaderAssistant,
)


class Command(BaseCommand):
    """
    Load SprayOperators from a CSV file command.
    """

    help = _("Load spray operators")

    def add_arguments(self, parser):
        parser.add_argument("csv_file", metavar="FILE")

    def handle(self, *args, **options):
        if "csv_file" not in options:
            raise CommandError(_("Missing spray operators csv file path"))
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
                            spray_operator, created = SprayOperator.objects.get_or_create(  # noqa pylint: disable=line-too-long
                                code=row["code"].strip(), name=row["name"]
                            )
                        except IntegrityError:
                            spray_operator = SprayOperator.objects.get(
                                code=row["code"]
                            )
                            spray_operator.name = row["name"]
                            spray_operator.save()
                            self.stdout.write(
                                "{} spray operator code already "
                                "exists.".format(row["code"].strip())
                            )
                        else:
                            if created:
                                print(row)
                        codes.append(row["code"])
                        self._add_team_leader_assistant(
                            spray_operator, row.get("team_leader_assistant")
                        )
                        self._add_team_leader(
                            spray_operator, row.get("team_leader")
                        )
                        self._add_location(
                            spray_operator, row.get("health_facility")
                        )
                    print(
                        SprayOperator.objects.exclude(code__in=codes).delete()
                    )

    def _add_team_leader_assistant(self, spray_operator, team_code):
        if team_code:
            try:
                team_leader = TeamLeaderAssistant.objects.get(  # noqa pylint: disable=line-too-long
                    code=team_code.strip()
                )
            except TeamLeaderAssistant.DoesNotExist:
                self.stderr.write("TLA {} does not exist".format(team_code))
            else:
                spray_operator.team_leader_assistant = team_leader
                spray_operator.save()

    def _add_team_leader(self, spray_operator, team_code):
        if team_code:
            try:
                team_leader = TeamLeader.objects.get(code=team_code.strip())
            except TeamLeader.DoesNotExist:
                self.stderr.write("TL {} does not exist".format(team_code))
            else:
                spray_operator.team_leader = team_leader
                spray_operator.save()

    def _add_location(self, spray_operator, health_facility):
        if health_facility:
            try:
                health_facility = Location.objects.get(
                    code=health_facility.strip(), level="RHC"
                )
            except Location.DoesNotExist:
                self.stderr.write(
                    "Catchment {} does not exist".format(health_facility)
                )
            else:
                spray_operator.rhc = health_facility
                spray_operator.district = health_facility.parent
                spray_operator.save()
