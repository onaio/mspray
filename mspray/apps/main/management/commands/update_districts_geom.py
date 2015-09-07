from django.contrib.gis.geos import MultiPolygon
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _('Set district geom from target areas geom')

    def handle(self, *args, **options):
        for district in Location.objects.filter(level='district'):
            tas = Location.objects.filter(parent=district).exclude(geom=None)
            if district.geom is None:
                items = []
                for ta in tas:
                    for poly in ta.geom:
                        items.append(poly)
                if len(items):
                    district.geom = MultiPolygon(items)
                    district.save()
                    self.stdout.write("Saved {} with {} items".format(
                        district.name, len(items)
                    ))
