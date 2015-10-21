from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import Location
from mspray.apps.main.tasks import link_spraypoint_with_osm
from mspray.apps.main.models.spray_day import STRUCTURE_GPS_FIELD
from mspray.apps.main.models.spray_day import NON_STRUCTURE_GPS_FIELD
from mspray.apps.main.utils import geojson_from_gps_string


class Command(BaseCommand):
    help = _('Set location based on target area field in data')

    def new_structure_gps(self, sprayday):
        data = sprayday.data
        gps_field = data.get(STRUCTURE_GPS_FIELD,
                             data.get(NON_STRUCTURE_GPS_FIELD))
        geom = geojson_from_gps_string(gps_field) \
            if gps_field is not None else None
        if geom is not None:
            locations = Location.objects.filter(
                geom__contains=geom,
                level=settings.MSPRAY_TA_LEVEL
            )
            if locations:
                location = locations[0]
                if settings.OSM_SUBMISSIONS and geom is not None:
                    sprayday.geom = geom
                    sprayday.bgeom = sprayday.geom.buffer(0.00004, 1)
                    sprayday.location = location
                    sprayday.save()

        return sprayday

    def link_spray_point(self, sprayday):
        try:
            pk = link_spraypoint_with_osm(sprayday.pk)
        except Exception as e:
            self.stderr.write("{}: {}".format(sprayday.pk, e))
        else:
            if pk == sprayday.pk:
                sp = SprayDay.objects.get(pk=pk)
                if sp.location is not None:
                    self.count += 1
                else:
                    sp = self.new_structure_gps(sp)
                    if sp.location is not None:
                        self.count += 1

    def handle(self, *args, **options):
        self.count = 0
        points = SprayDay.objects.filter(location=None)
        final_count = points.count()
        for sprayday in points.iterator():
            ta = sprayday.data.get('target_area')
            district = sprayday.data.get('district')
            osm_structure = sprayday.data.get('osmstructure')
            try:
                location = Location.objects.get(name=ta.replace('_', ' / '),
                                                parent__code=district)
                if not osm_structure:
                    sprayday.location = location
                    sprayday.save()
                    self.count += 1
                else:
                    self.link_spray_point(sprayday)
            except Location.DoesNotExist:
                self.link_spray_point(sprayday)

        self.stdout.write(
            "{} points of {} linked to location.".format(
                self.count, final_count
            )
        )
