from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models import Sum
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _("Update location structure numbers for districts/regions"
             " from target areas")

    def handle(self, *args, **options):
        def _update_location_structures(level):
            for loc in Location.objects.filter(level=level).iterator():
                structures = \
                    loc.location_set.aggregate(s=Sum('structures'))['s']
                if structures:
                    loc.structures = structures
                    loc.save()

        def _update_spray_areas_structures():
            for loc in Location.objects.filter(level='ta')\
                    .annotate(num_structures=Count('household'))\
                    .filter(num_structures__gt=0).iterator():
                loc.structures = loc.num_structures
                loc.save()

        def _update_num_of_spray_areas():
            for loc in Location.objects.filter(level='RHC')\
                    .annotate(nm_ta=Count('location')):
                loc.num_of_spray_areas = loc.nm_ta
                loc.save()

            for loc in Location.objects.filter(level='RHC')\
                    .values('parent').annotate(num_ta=Count('location')):
                district = Location.objects.get(pk=loc.get('parent'))
                district.num_of_spray_areas = loc.get('num_ta')
                district.save()

        _update_spray_areas_structures()
        for level in ['RHC', 'district']:
            _update_location_structures(level)

        _update_num_of_spray_areas()
