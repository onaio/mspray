import os

from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from mspray.apps.main.osm import parse_osm
from mspray.apps.main.models import Household
from mspray.apps.main.models import Location


def process_osm_file(path):
    with open(path) as f:
        content = f.read()
        nodes = parse_osm(content.strip())
        ways = [
            way for way in nodes
            if not way.get('osm_id').startswith('-')
            and way.get('osm_type') == 'way'
        ]
        if ways:
            for way in ways:
                location = Location.objects.filter(
                    geom__contains=ways[0].get('geom'),
                    level='ta'
                ).first()
                if location:
                    try:
                        Household.objects.create(
                            hh_id=way.get('osm_id'),
                            geom=way.get('geom').centroid,
                            bgeom=way.get('geom'),
                            data=way.get('tags'),
                            location=location
                        )
                    except Household.DoesNotExist:
                        pass
                    except IntegrityError:
                        pass


class Command(BaseCommand):
    help = _('Link spray operator ans team leader to spray data.')

    def add_arguments(self, parser):
        parser.add_argument(dest='osmfolder',
                            help='osm file')

    def handle(self, *args, **options):
        osmfile = options.get('osmfolder')
        if osmfile:
            if os.path.isdir(osmfile):
                entries = os.scandir(os.path.dirname(osmfile))
                for entry in entries:
                    is_osm_file = entry.name.endswith('.osm') \
                        or entry.name.endswith('.xml')
                    is_file = entry.is_file()
                    if not is_osm_file or (is_osm_file and not is_file):
                        continue
                    count = Household.objects.count()
                    process_osm_file(entry.path)
                    after_count = Household.objects.count()
                    self.stdout.write('%d structures added.' %
                                      (after_count - count))
            else:
                path = os.path.abspath(osmfile)
                count = Household.objects.count()
                process_osm_file(path)
                after_count = Household.objects.count()
                self.stdout.write('%d structures added.' %
                                  (after_count - count))
