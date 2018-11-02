import os

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import MultiPoint
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal import SpatialReference
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Household
from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _('Load locations')

    def add_arguments(self, parser):
        parser.add_argument('shape_file', metavar="FILE")
        parser.add_argument('--code',
                            dest='code',
                            default='OBJECTID',
                            help="code field to use in the shape file")
        parser.add_argument('--code-int',
                            dest='code_is_integer',
                            action='store_true',
                            help="Coerce the code value to integer")

    def handle(self, *args, **options):
        if 'shape_file' not in options:
            raise CommandError(_('Missing locations shape file path'))
        else:
            try:
                path = os.path.abspath(options['shape_file'])
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                pre_create = Household.objects.count()
                count = 0
                failed = 0
                srs = SpatialReference('+proj=longlat +datum=WGS84 +no_defs')
                ds = DataSource(path)
                layer = ds[0]
                locations = Location.objects.exclude(parent=None)\
                    .order_by('pk')
                code_field = options.get('code')

                for feature in layer:
                    geom = feature.geom.transform(srs, True)
                    point = GEOSGeometry(geom.centroid.wkt, srid=srs.srid)
                    polygon = GEOSGeometry(geom.wkt, srid=srs.srid)
                    try:
                        plocations = locations.filter(geom__covers=point)
                        blocations = locations.filter(geom__covers=polygon)
                        if plocations.count() and blocations.count():
                            location = blocations.first()
                            hh_id = feature.get(code_field)
                            Household.objects.create(
                                hh_id=hh_id,
                                geom=MultiPoint(point),
                                bgeom=polygon,
                                location=location
                            )
                            count += 1
                    except Location.DoesNotExist:
                        failed += 1
                        continue

                self.stdout.write("Updated {} failed {}".format(count, failed))
                created = Household.objects.count()
                self.stdout.write("Created {} households".format(
                    created - pre_create
                ))
