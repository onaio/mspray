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
        geom__contained=geom.wkt, level=parent_level
    ).first()

    if parent is None:
        parent = Location.objects.filter(
            geom__covers=geom.wkt, level=parent_level, name=parent_name
        ).first()
        if not parent:
            parent = Location.objects.filter(
                level=parent_level, name=parent_name
            ).first()
    else:
        assert parent.name == parent_name

    return parent


def get_parent_by_code(code, level):
    return Location.objects.filter(code=code, level=level).first()


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
            '--parent-skip',
            dest='skip_parent',
            default='no',
            help="skip parent if not found"
        )
        parser.add_argument(
            '--parent-code',
            dest='parent_code',
            help="parent name field to use in the shape file"
        )
        parser.add_argument(
            '--code',
            dest='code_field',
            default='fid',
            help="code field to use in the shape file"
        )
        parser.add_argument(
            '--skip',
            dest='skip_field',
            help="skip field to use in the shape file"
        )
        parser.add_argument(
            '--skipif',
            dest='skip_value',
            help="skip value to use to skip records in the shape file"
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
                skip_parent = options.get('skip_parent')
                parent_code_field = options.get('parent_code')
                structures_field = options['structures_field']

                skip_field = options.get('skip_field')
                skip_value = options.get('skip_value')
                if skip_field and not skip_value:
                    raise CommandError(_('Error: please provide skip value'))

                count = exception_raised = failed = skipped = updated = 0
                srs = SpatialReference('+proj=longlat +datum=WGS84 +no_defs')
                ds = DataSource(path)
                layer = ds[0]

                for feature in layer:
                    # skip
                    if skip_field and skip_value:
                        if feature.get(skip_field) == skip_value:
                            skipped += 1
                            continue

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
                        if code == 0:
                            skipped += 1
                            continue
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
                    name = name.strip()
                    parent_name = parent_name.strip()

                    if parent_code_field:
                        parent_code = feature.get(parent_code_field)
                        parent = get_parent_by_code(parent_code, parent_level)
                    else:
                        parent = get_parent(geom, parent_level, parent_name)

                    if skip_parent != 'yes' and not parent:
                        skipped += 1
                        continue
                    try:
                        location = Location.objects.get(
                            name=name, level=level, parent=parent
                        )
                    except Location.DoesNotExist:
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
                    else:
                        location.geom = geom.wkt
                        location.save()
                        updated += 1

                self.stdout.write(
                    "Created %s locations, %s updated, failed %s, skipped %s, "
                    "error %s" % (
                        count, updated, failed, skipped, exception_raised
                    )
                )
