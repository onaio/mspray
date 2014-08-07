import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main import utils


class Command(BaseCommand):
    args = '<path to shapefile>'
    help = _('Load an area shapefile')

    def handle(self, *args, **options):
        for path in args:
            try:
                path = os.path.abspath(path)
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                utils.load_area_layer_mapping(path, verbose=True)
                # utils.load_target_area_shapefile(path)
