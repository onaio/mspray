import os
import gc

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.libs.osm import clean_osm_file_with_db


class Command(BaseCommand):
    help = _('Clean the OSM files in a given directory.')

    def add_arguments(self, parser):
        parser.add_argument(dest='osmfolder', help='osm files directory')
        parser.add_argument(dest='outputfolder', help='output directory')

    def handle(self, *args, **options):
        osmfolder = options.get('osmfolder')
        outputfolder = options.get('outputfolder')

        if outputfolder is None:
            outputfolder = "/tmp/"

        if osmfolder and os.path.isdir(osmfolder):
            entries = os.scandir(os.path.dirname(osmfolder))
            for entry in entries:
                is_osm_file = entry.name.endswith('.osm') \
                    or entry.name.endswith('.xml')
                is_file = entry.is_file()
                if not is_osm_file or (is_osm_file and not is_file):
                    continue
                output_file = os.path.join(outputfolder, entry.name)
                result = clean_osm_file_with_db(entry.path, output_file)
                self.stdout.write('{} structures removed from {}.'.format(
                    result, entry.name))
                gc.collect()
