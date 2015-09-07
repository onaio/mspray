import os

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _('Load locations')

    def add_arguments(self, parser):
        parser.add_argument('csv_file', metavar="FILE")
        parser.add_argument('--code',
                            dest='code',
                            default='ADM1_NAME',
                            help="code field to use in the shape file")

    def handle(self, *args, **options):
        if 'csv_file' not in options:
            raise CommandError(_('Missing locations shape file path'))
        else:
            try:
                path = os.path.abspath(options['csv_file'])
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                code = options['code']
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
