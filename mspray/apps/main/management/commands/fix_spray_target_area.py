from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import Location
from mspray.apps.main.tasks import link_spraypoint_with_osm


class Command(BaseCommand):
    help = _('Set location based on target area field in data')

    def handle(self, *args, **options):
        count = 0
        points = SprayDay.objects.filter(location=None)
        final_count = points.count()
        for sprayday in points.iterator():
            ta = sprayday.data.get('target_area')
            osm_structure = sprayday.data.get('osmstructure')
            try:
                location = Location.objects.get(name=ta.replace('_', ' / '))
                if not osm_structure:
                    sprayday.location = location
                    sprayday.save()
                    count += 1
                else:
                    pk = link_spraypoint_with_osm(sprayday.pk)
                    if pk == sprayday.pk:
                        sp = SprayDay.objects.get(pk=pk)
                        if sp.location is not None:
                            count += 1
            except Location.DoesNotExist:
                pass

        self.stdout.write(
            "{} points of {} linked to location.".format(
                count, final_count
            )
        )
