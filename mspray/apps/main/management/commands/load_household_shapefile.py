import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main import utils


class Command(BaseCommand):
    args = '<path to shapefile>'
    help = _('Load a household shapefile')

    def add_arguments(self, parser):
        parser.add_argument('shape_file', metavar="FILE")

    def handle(self, *args, **options):
        if 'shape_file' not in options:
            raise CommandError(_('Missing locations shape file path'))
        else:
            try:
                path = os.path.abspath(options['shape_file'])
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                utils.load_household_layer_mapping(path, verbose=True)
