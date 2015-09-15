from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Household
from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _('Check locations structures')

    def handle(self, *args, **options):
        matching = 0
        for location in Location.objects.filter().iterator():
            hh = Household.objects.filter(geom__coveredby=location.geom)
            count = hh.count()
            match = location.structures == count
            if not match:
                self.stdout.write(
                    "Location: {} has {} hhs, should probably be {}"
                    .format(location.name, location.structures, count)
                )
            else:
                matching += 1

        self.stdout.write("{} Matches of {}.".format(
            matching, Location.objects.count()
        ))
