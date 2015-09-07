import os

from django.contrib.gis.gdal import geometries
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
        parser.add_argument('--code-int',
                            dest='code_is_integer',
                            action='store_true',
                            help="Coerce the code value to integer")

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
                code_is_integer = options['code_is_integer']
                count = 0
                failed = 0
                ds = DataSource(path)
                layer = ds[0]

                for feature in layer:
                    name = feature.get(code)
                    name = int(name) if code_is_integer else name
                    try:
                        location = Location.objects.get(code=name)
                    except Location.DoesNotExist:
                        failed += 1
                        continue
                    else:
                        if isinstance(feature.geom, geometries.Polygon):
                            geom = geometries.MultiPolygon('MULTIPOLYGON',
                                                           srs=layer.srs)
                            geom.add(feature.geom)
                        else:
                            geom = feature.geom
                        location.geom = geom.wkt
                        location.save()
                        count += 1

                self.stdout.write("Updated {} locations, failed {}".format(
                    count, failed
                ))
