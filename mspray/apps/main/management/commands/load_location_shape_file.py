import os

from django.contrib.gis.gdal import geometries
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal import SpatialReference
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


def get_or_create_parent(district_name, level='district'):
    try:
        location = Location.objects.get(
            name__iexact=district_name, level=level
        )
    except Location.DoesNotExist:
        code = Location.objects.filter(level=level).count()
        rank = code = 1 if code == 0 else code + 1
        location = Location.objects.create(
            name=district_name, code=code, rank=rank, level=level
        )

    return location


class Command(BaseCommand):
    help = _('Load locations')

    def add_arguments(self, parser):
        parser.add_argument('shape_file', metavar="FILE")
        parser.add_argument('to_spray')
        parser.add_argument('district_name')
        parser.add_argument('code')
        parser.add_argument('rank')
        parser.add_argument('homesteads')
        parser.add_argument('structures')

    def handle(self, *args, **options):
        if 'shape_file' not in options:
            raise CommandError(_('Missing locations shape file path'))
        else:
            try:
                path = os.path.abspath(options['shape_file'])
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                count = exception_raised = failed = skipped = 0
                srs = SpatialReference('+proj=longlat +datum=WGS84 +no_defs')
                ds = DataSource(path)
                layer = ds[0]
                district_name_field = options.get('district_name')
                code_field = options.get('code')
                rank_field = options.get('rank')
                homesteads_field = options.get('homesteads')
                structures_field = options.get('structures')
                to_spray = options.get('to_spray')

                for feature in layer:
                    spray = int(feature.get(to_spray))
                    if spray == 0:
                        skipped += 1
                        continue

                    district_name = feature.get(district_name_field)
                    code = int(feature.get(code_field))
                    rank = int(feature.get(rank_field))
                    homesteads = int(feature.get(homesteads_field))
                    structures = \
                        int(feature.get(structures_field)) * homesteads
                    name = '%s_%s' % (code, rank)
                    parent = get_or_create_parent(district_name)
                    if isinstance(feature.geom, geometries.Polygon):
                        geom = geometries.MultiPolygon('MULTIPOLYGON', srs=srs)
                        geom.add(feature.geom.transform(srs, True))
                    else:
                        geom = feature.geom.transform(srs, True)
                    try:
                        Location.objects.create(
                            name=name, code=code, rank=rank,
                            homesteads=homesteads, structures=structures,
                            level='ta', parent=parent, geom=geom.wkt
                        )
                    except IntegrityError:
                        failed += 1
                    except Exception as e:
                        exception_raised += 1
                    else:
                        count += 1

                self.stdout.write(
                    "Created %s locations, failed %s, skipped %s, error %s" % (
                        count, failed, skipped, exception_raised
                    )
                )
