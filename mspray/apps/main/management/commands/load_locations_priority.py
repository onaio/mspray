# -*- coding=utf-8 -*-
"""
Load a CSV file with location priority.
"""
import codecs
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    """
    Load a CSV file with location priority.
    """

    help = _("Load a CSV file with location priority.")

    def add_arguments(self, parser):
        parser.add_argument("csv_file", metavar="FILE")

    def handle(self, *args, **options):
        if "csv_file" not in options:
            raise CommandError(_("Missing csv file path"))
        else:
            try:
                path = os.path.abspath(options["csv_file"])
            except FileNotFoundError as error:
                raise CommandError(_("Error: %(msg)s" % {"msg": error}))
            else:
                with codecs.open(path, encoding="utf-8") as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        name = row.get("SPRAYAREA")
                        if name:
                            try:
                                spray_area = Location.objects.get(name=name)
                            except Location.DoesNotExist:
                                # fail silently
                                pass
                            else:
                                priority = row.get("Priority")
                                if priority:
                                    spray_area.priority = priority
                                    spray_area.save()
