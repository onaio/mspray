from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location
from mspray.apps.reactive.irs.utils import create_chw_object_from_location

level = getattr(settings, "MSPRAY_REACTIVE_IRS_CHW_LOCATION_LEVEL", "chw")


class Command(BaseCommand):
    help = _("Creates Community Health Worker objects from a location objects")

    def handle(self, *args, **options):
        locations = Location.objects.filter(level=level)
        self.stdout.write(f"Going to process {locations.count()} locations")
        for location in locations:
            create_chw_object_from_location(location)
            self.stdout.write(f"Done with {location.name} successfully")
