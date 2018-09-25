# -*- coding=utf-8 -*-
"""
Load SprayOperators from a CSV file.
"""
import codecs
import csv
import os

from django.db import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import (
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
                    for row in csv_reader:
                        try:
                            spray_operator, created = SprayOperator.objects.get_or_create(
                                code=row["code"].strip(), name=row["name"]
                            )
                        except IntegrityError:
                            self.stdout.write(
                                "{} spray operator code already "
                                "exists.".format(row["code"].strip())
                            )
                        else:
                            if created:
                                print(row)
                            team_code = row["team_leader_assistant"].strip()
                            if team_code:
                                try:
                                    team_leader = TeamLeaderAssistant.objects.get(
                                        code=team_code
                                    )
                                except TeamLeaderAssistant.DoesNotExist:
                                    self.stderr.write("TLA {} does not exist"
                                                      .format(team_code))
                                else:
                                    spray_operator.team_leader_assistant = (
                                        team_leader
                                    )
                                    spray_operator.save()
                            team_code = row["team_leader"].strip()
                            if team_code:
                                try:
                                    team_leader = TeamLeader.objects.get(
                                        code=team_code
                                    )
                                except TeamLeader.DoesNotExist:
                                    self.stderr.write("TL {} does not exist"
                                                      .format(team_code))
                                    pass
                                else:
                                    spray_operator.team_leader = team_leader
                                    spray_operator.save()
