from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay
from mspray.apps.main.utils import geojson_from_gps_string


class Command(BaseCommand):
    args = '<path to shapefile>'
    help = _('Load locations')

    def handle(self, *args, **options):
        gps_field = settings.MSPRAY_STRUCTURE_GPS_FIELD
        count = 0

        for spraypoint in SprayDay.objects.filter(location=None).iterator():
            gps = spraypoint.data.get(gps_field)
            if gps:
                geom = geojson_from_gps_string(gps)
                if geom:
                    location = Location.objects.filter(
                        geom__contains=geom,
                        level=settings.MSPRAY_TA_LEVEL
                    ).first()
                    if location:
                        spraypoint.geom = geom
                        spraypoint.bgeom = spraypoint.geom.buffer(0.00004, 1)
                        spraypoint.location = location
                        spraypoint.save()
                        count += 1

        print("Updated {} spraypoints".format(count))
