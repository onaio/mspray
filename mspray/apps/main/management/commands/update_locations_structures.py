from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _("Update location structure numbers for districts/regions"
             " from target areas")

    def handle(self, *args, **options):
        def _update_location_level(level):
            for loc in Location.objects.filter(level=level).iterator():
                structures = \
                    loc.location_set.aggregate(s=Sum('structures'))['s']
                if structures:
                    loc.structures = structures

                loc.num_of_spray_areas = Location.objects.filter(
                    geom__contained=loc.geom, level='ta'
                ).count()
                loc.save()

        for level in ['RHC', 'district']:
            _update_location_level(level)
