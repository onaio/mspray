import os

from django.contrib.gis.gdal import geometries
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal import SpatialReference
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


def get_parent(geom, parent_level, parent_name):
    parent = Location.objects.filter(
        geom__bbcontains=geom.wkt, level=parent_level
    ).first()

    if parent is None:
        parent = Location.objects.filter(
            geom__intersects=geom.wkt, level=parent_level, name=parent_name
        ).first()

    return parent


class Command(BaseCommand):
    help = _('Load locations')

    def add_arguments(self, parser):
        parser.add_argument('shape_file', metavar="FILE")
        parser.add_argument(
            'name_field',
            help="name field to use in the shape file"
        )
        parser.add_argument(
            'level',
        )
        parser.add_argument(
            '--structures',
            dest='structures_field',
            default='structures',
            help="# of structure field to use in the shape file"
        )
        parser.add_argument(
            '--parent',
            dest='parent_field',
            default='parent',
            help="parent name field to use in the shape file"
        )
        parser.add_argument(
            '--parent-level',
            dest='parent_level',
            default='parent_level',
            help="parent name field to use in the shape file"
        )
        parser.add_argument(
            '--code',
            dest='code_field',
            default='fid',
            help="code field to use in the shape file"
        )

    def handle(self, *args, **options):
        if 'shape_file' not in options:
            raise CommandError(_('Missing locations shape file path'))
        else:
            try:
                path = os.path.abspath(options['shape_file'])
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                code_field = options['code_field']
                level = options['level']
                name_field = options['name_field']
                parent_field = options['parent_field']
                parent_level = options['parent_level']
                structures_field = options['structures_field']
                count = exception_raised = failed = skipped = 0
                srs = SpatialReference('+proj=longlat +datum=WGS84 +no_defs')
                ds = DataSource(path)
                layer = ds[0]

                for feature in layer:
                    if isinstance(feature.geom, geometries.Polygon):
                        geom = geometries.MultiPolygon('MULTIPOLYGON', srs=srs)
                        geom.add(feature.geom.transform(srs, True))
                    else:
                        geom = feature.geom.transform(srs, True)
                    name = feature.get(name_field)
                    if code_field == 'fid':
                        code = feature.fid + 1
                    else:
                        code = int(feature.get(code_field))
                    if bytearray(structures_field.encode('utf8')) in \
                            feature.fields:
                        structures = int(feature.get(structures_field))
                    else:
                        structures = 0
                    if bytearray(parent_field.encode('utf8')) in \
                            feature.fields:
                        parent_name = feature.get(parent_field)
                    else:
                        parent_name = name

                    parent = get_parent(geom, parent_level, parent_name)
                    try:
                        Location.objects.create(
                            name=name, code=code, structures=structures,
                            level=level, parent=parent, geom=geom.wkt
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