import os

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from mspray.apps.main.models import Household
from mspray.apps.main.tasks import process_osm_file


class Command(BaseCommand):
    help = _("Link spray operator ans team leader to spray data.")

    def add_arguments(self, parser):
        parser.add_argument(dest="osmfolder", help="osm file")

    def handle(self, *args, **options):
        osmfile = options.get("osmfolder")
        if osmfile:
            if os.path.isdir(osmfile):
                entries = os.scandir(osmfile)
                for entry in entries:
                    is_osm_file = entry.name.endswith(
                        ".osm"
                    ) or entry.name.endswith(".xml")
                    is_file = entry.is_file()
                    if not is_osm_file or (is_osm_file and not is_file):
                        continue
                    count = Household.objects.count()
                    process_osm_file.delay(entry.path)
                    after_count = Household.objects.count()
                    self.stdout.write(
                        "{} structures added from {}.".format(
                            (after_count - count), entry.name
                        )
                    )
            else:
                path = os.path.abspath(osmfile)
                count = Household.objects.count()
                process_osm_file(path)
                after_count = Household.objects.count()
                self.stdout.write(
                    "{} structures added from {}.".format(
                        (after_count - count), osmfile
                    )
                )
