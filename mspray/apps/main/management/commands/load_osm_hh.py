# -*- coding: utf-8 -*-
"""load_osm_hh command

Loads OSM files as households into the Household model.
"""
import os

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Household
from mspray.apps.main.tasks import process_osm_file


def handle_osm_file(path, is_async, stdout):
    """Process an OSM file.

    Arguments:
    ----------
    path - file path to an OSM file.
    is_async - boolean of whether to process file asynchronously or not.
    stdout - standard output to print progress to
    """
    count = Household.objects.count()
    if is_async:
        process_osm_file.delay(path)
    else:
        process_osm_file(path)
    after_count = Household.objects.count()
    stdout.write(
        "{} structures added from {}.".format((after_count - count), path)
    )


def handle_osm_directory(osm_directory, is_async, stdout):
    """Process OSM directory with OSM files.

    Arguments:
    ----------
    osm_directory - path to an OSM directory
    is_async - boolean of whether to process file asynchronously or not.
    stdout - standard output to print progress to
    """
    if os.path.isdir(osm_directory):
        entries = os.scandir(osm_directory)
        for entry in entries:
            if os.path.isdir(entry.path):
                handle_osm_directory(entry.path, is_async, stdout)
            else:
                is_osm_file = entry.name.endswith(
                    ".osm"
                ) or entry.name.endswith(".xml")
                is_file = entry.is_file()
                if not is_osm_file or (is_osm_file and not is_file):
                    continue
                handle_osm_file(entry.path, is_async, stdout)


class Command(BaseCommand):
    """Load OSM files as households. """

    help = _("Load OSM files as households from a directory of OSM filesa.")

    def add_arguments(self, parser):
        parser.add_argument(dest="osmfolder", help="osm file")
        parser.add_argument(
            "--async",
            action="store_true",
            dest="is_async",
            help="Whether to process asynchronously",
        )

    def handle(self, *args, **options):
        osmfile = options.get("osmfolder")
        is_async = options.get("is_async")
        if osmfile:
            if os.path.isdir(osmfile):
                handle_osm_directory(osmfile, is_async, self.stdout)
            else:
                path = os.path.abspath(osmfile)
                handle_osm_file(path, is_async, self.stdout)
