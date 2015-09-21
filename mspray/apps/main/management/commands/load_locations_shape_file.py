import os

from django.conf import settings
from django.contrib.gis.gdal import geometries
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal import SpatialReference
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _('Load locations')

    def add_arguments(self, parser):
        parser.add_argument('shape_file', metavar="FILE")
        parser.add_argument('--code',
                            dest='code',
                            default='ADM1_NAME',
                            help="code field to use in the shape file")
        parser.add_argument('--code-int',
                            dest='code_is_integer',
                            action='store_true',
                            help="Coerce the code value to integer")

    def _get_location(self, feature, code, code_is_integer=False):
        name = feature.get(code)
        name = int(name) if code_is_integer else name
        if settings.SITE_NAME == 'zambia':
            location = self._get_zambia_location(feature, code)
        else:
            location = Location.objects.get(code=name)

        return location

    def _get_zambia_location(self, feature, code):
        district = feature.get('district_1')
        structures = int(feature.get('structur_1'))
        name = feature.get('psa_id_1')
        loc_code = feature.get(code)

        try:
            location = Location.objects.get(code=name, parent__name=district)
        except Location.DoesNotExist:
            parent = Location.objects.get(name=district)
            location = Location.objects.create(
                name=name,
                code=loc_code,
                structures=structures,
                parent=parent,
                level=settings.MSPRAY_TA_LEVEL
            )

        return location

    def handle(self, *args, **options):
        if 'shape_file' not in options:
            raise CommandError(_('Missing locations shape file path'))
        else:
            try:
                path = os.path.abspath(options['shape_file'])
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                code = options['code']
                code_is_integer = options['code_is_integer']
                count = 0
                failed = 0
                srs = SpatialReference('+proj=longlat +datum=WGS84 +no_defs')
                ds = DataSource(path)
                layer = ds[0]

                for feature in layer:
                    if feature.get('manual_c_1') != 'Targeted':
                        continue
                    try:
                        location = self._get_location(
                            feature, code, code_is_integer
                        )
                    except Location.DoesNotExist:
                        failed += 1
                        continue
                    else:
                        if isinstance(feature.geom, geometries.Polygon):
                            geom = geometries.MultiPolygon('MULTIPOLYGON',
                                                           srs=srs)
                            geom.add(feature.geom.transform(srs, True))
                        else:
                            geom = feature.geom.transform(srs, True)
                        location.geom = geom.wkt
                        location.save()
                        count += 1

                self.stdout.write("Updated {} locations, failed {}".format(
                    count, failed
                ))
