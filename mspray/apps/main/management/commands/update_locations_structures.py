from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _("Update location structure numbers for districts/regions"
             " from target areas")

    def handle(self, *args, **options):
        locations = Location.objects.filter(structures__gt=0)\
            .exclude(parent=None)\
            .values('parent').annotate(total_structures=Sum('structures'))\
            .values_list('total_structures', 'parent')

        for structures, parent in locations:
            location = Location.objects.get(pk=parent)
            location.structures = structures
            location.save()

        print("Updated {} Locations".format(len(locations)))
