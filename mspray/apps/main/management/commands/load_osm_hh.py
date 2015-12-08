import csv
import os

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from mspray.apps.main.osm import parse_osm


class Command(BaseCommand):
    help = _('Link spray operator ans team leader to spray data.')

    def add_arguments(self, parser):
        parser.add_argument(dest='osmfile', help='osm file')

    def handle(self, *args, **options):
        osmfile = options.get('osmfile')
        path = '/tmp/osmdata.csv'
        if osmfile:
            if os.path.exists(path):
                os.remove(path)
            with open(path, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
                headers = [
                    'target_area', 'osm_id', 'osm', 'building', 'x', 'y',
                    'shape_area', 'shape_leng', 'wkt'
                ]
                writer.writerow(headers)
                for entry in os.scandir(os.path.dirname(osmfile)):
                    is_osm_file = entry.name.endswith('osm')
                    is_file = entry.is_file()
                    if not is_osm_file or (is_osm_file and not is_file):
                        continue
                    self.stdout.write(entry.name)

                    with open(entry.path) as f:
                        content = f.read()
                        nodes = parse_osm(content.strip())
                        nodes = list(filter(
                            lambda x:
                            x.get('osm_type') == 'node',
                            nodes
                        ))
                        ta = entry.name.replace('.osm', '')[3:]

                        for node in nodes:
                            geom = node.get('geom')
                            tags = node.get('tags')
                            building = tags.get('id2')
                            shape_area = tags.get('Shape_Area')
                            shape_length = tags.get('Shape_Leng')
                            osm_id = node.get('osm_id')
                            osm_type = node.get('osm_type')
                            osm_name = 'OSM{}{}'.format(osm_type, osm_id)
                            ta = tags.get('id') or ta

                            writer.writerow([
                                ta,
                                osm_id,
                                osm_name,
                                building,
                                geom.centroid.x,
                                geom.centroid.y,
                                shape_area,
                                shape_length,
                                geom.wkt
                            ])
