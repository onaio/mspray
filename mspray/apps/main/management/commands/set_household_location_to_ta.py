from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Household
from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _('Set target area location for households')

    def handle(self, *args, **options):
        self.stdout.write("Starting...")
        count = 0
        locations = Location.objects.filter(level=settings.MSPRAY_TA_LEVEL)
        total = locations.count()
        for location in locations.iterator():
            if location.geom is not None:
                hh = Household.objects.filter(geom__coveredby=location.geom)
                hh.update(location=location)
                count += 1
                self.stdout.write("Handling {} of {}".format(count, total))

        self.stdout.write("Done.")
