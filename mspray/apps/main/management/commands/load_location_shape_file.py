# -*- coding=utf-8 -*-
"""
load_location_shapefile command - loads districts, health facility catchment
area and spray area shapefiles.
"""
import os

from django.contrib.gis.gdal import DataSource, SpatialReference, geometries
from django.contrib.gis.gdal.error import GDALException
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


def get_parent(geom, parent_level, parent_name):
    """
    Return a location/parent of the provided geom object, parent_level and
    parent_name. geom is used first and if that fails the parent name is used.
    In both cases the parent level is used to limit the results.
    """
    parent = Location.objects.filter(
        geom__covers=geom.wkt, level=parent_level
    ).first()

    if parent is None:
        parent = Location.objects.filter(
            geom__covers=geom.wkt, level=parent_level, name=parent_name
        ).first()
        if not parent:
            parent = Location.objects.filter(
                level=parent_level, name=parent_name
            ).first()
    # else:
    #     assert parent.name == parent_name

    return parent


def get_parent_by_code(code, level):
    """
    Get parent location by code given the level.
    """
    return Location.objects.filter(code=code, level=level).first()


class Command(BaseCommand):
    """
    Uploads location information from a shapefile.
    """

    help = _("Load locations")

    def add_arguments(self, parser):
        parser.add_argument("shape_file", metavar="FILE",
                            help="The file path to the shapefile")
        parser.add_argument(
            "name_field", help="name field to use in the shapefile"
        )
        parser.add_argument("level")
        parser.add_argument(
            "--structures",
            dest="structures_field",
            default="structures",
            help="# of structure field to use in the shape file",
        )
        parser.add_argument(
            "--parent",
            dest="parent_field",
            default="parent",
            help="parent name field to use in the shape file",
        )
        parser.add_argument(
            "--parent-level",
            dest="parent_level",
            default="parent_level",
            help="parent name field to use in the shape file",
        )
        parser.add_argument(
            "--parent-skip",
            dest="skip_parent",
            default="no",
            help="skip parent if not found",
        )
        parser.add_argument(
            "--parent-code",
            dest="parent_code",
            help="parent name field to use in the shape file",
        )
        parser.add_argument(
            "--code",
            dest="code_field",
            default="fid",
            help="code field to use in the shape file",
        )
        parser.add_argument(
            "--skip",
            dest="skip_field",
            help="skip field to use in the shape file",
        )
        parser.add_argument(
            "--skipif",
            dest="skip_value",
            help="skip value to use to skip records in the shape file",
        )

    def handle(self, *args, **options):  # pylint: disable=R0912,R0914,R0915
        if "shape_file" not in options:
            raise CommandError(_("Missing locations shape file path"))
        else:
            try:
                path = os.path.abspath(options["shape_file"])
            except Exception as error:
                raise CommandError(_("Error: %(msg)s" % {"msg": error}))
            else:
                code_field = options["code_field"]
                level = options["level"]
                name_field = options["name_field"]
                parent_field = options["parent_field"]
                parent_level = options["parent_level"]
                skip_parent = options.get("skip_parent")
                parent_code_field = options.get("parent_code")
                structures_field = options["structures_field"]

                skip_field = options.get("skip_field")
                skip_value = options.get("skip_value")
                if skip_field and not skip_value:
                    raise CommandError(_("Error: please provide skip value"))
                skip_value = (
                    int(skip_value) if skip_value is not None else None
                )

                count = exception_raised = failed = skipped = updated = 0
                srs = SpatialReference("+proj=longlat +datum=WGS84 +no_defs")
                data_source = DataSource(path)
                layer = data_source[0]

                for feature in layer:
                    # skip
                    if skip_field and skip_value is not None:
                        if feature.get(skip_field) == skip_value:
                            skipped += 1
                            self.stdout.write(
                                "Skipping %s - skip." % feature.get(name_field)
                            )
                            continue

                    try:
                        is_polygon = isinstance(
                            feature.geom, geometries.Polygon
                        )
                    except GDALException as error:
                        self.stderr.write("Error: %s" % error)
                        continue

                    if is_polygon:
                        geom = geometries.MultiPolygon("MULTIPOLYGON", srs=srs)
                        geom.add(feature.geom.transform(srs, True))
                    else:
                        geom = feature.geom.transform(srs, True)
                    name = feature.get(name_field)
                    if code_field == "fid":
                        code = feature.fid + 1
                    else:
                        code = int(feature.get(code_field))
                        if code == 0:
                            skipped += 1
                            self.stdout.write(
                                "Skipping %s - code." % feature.get(name_field)
                            )
                            continue
                    if (
                        bytearray(structures_field.encode("utf8"))
                        in feature.fields
                    ):
                        structures = int(feature.get(structures_field))
                    else:
                        structures = 0
                    if (
                        bytearray(parent_field.encode("utf8"))
                        in feature.fields
                    ):
                        parent_name = feature.get(parent_field)
                    elif parent_field in feature.fields:
                        parent_name = feature.get(parent_field)
                    else:
                        parent_name = name
                    name = name.strip()
                    parent_name = parent_name.strip()

                    if skip_parent == "yes":
                        self.stdout.write(f"No parent for {name}.")
                        parent = None
                    else:
                        if parent_code_field:
                            parent_code = feature.get(parent_code_field)
                            parent = get_parent_by_code(
                                parent_code, parent_level)
                        else:
                            parent = get_parent(
                                geom, parent_level, parent_name)

                        if not parent:
                            self.stdout.write(
                                f"Skipping {name_field} - parent.")
                            skipped += 1
                            continue

                    try:
                        target = feature.get("TARGET") in [1, 2]
                    except IndexError:
                        target = True
                    try:
                        location = Location.objects.get(
                            name=name, level=level, parent=parent
                        )
                    except Location.DoesNotExist:
                        try:
                            Location.objects.create(
                                name=name,
                                code=code,
                                structures=structures,
                                level=level,
                                parent=parent,
                                geom=geom.wkt,
                                target=target,
                            )
                        except IntegrityError:
                            failed += 1
                        except Exception:  # pylint: disable=broad-except
                            exception_raised += 1
                        else:
                            count += 1
                    else:
                        if level == "RHC" and code != location.code:
                            location.code = code
                        location.target = target
                        location.geom = geom.wkt
                        try:
                            location.save()
                        except IntegrityError:
                            pass
                        else:
                            updated += 1

                self.stdout.write(
                    "Created %s locations, %s updated, failed %s, skipped %s, "
                    "error %s"
                    % (count, updated, failed, skipped, exception_raised)
                )
