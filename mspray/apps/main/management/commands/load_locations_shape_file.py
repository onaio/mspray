import os

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    args = '<path to shapefile>'
    help = _('Load locations')

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError(_('Missing locations shape file path'))
        for path in args:
            try:
                path = os.path.abspath(path)
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                code = 'ADM1_NAME'
                count = 0
                ds = DataSource(path)
                layer = ds[0]

                for feature in layer:
                    name = feature.get(code)
                    try:
                        location = Location.objects.get(code=name)
                    except Location.DoesNotExist:
                        continue
                    else:
                        location.geom = feature.geom.wkt
                        location.save()
                        count += 1

                print("Updated {} locations".format(count))
