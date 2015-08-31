from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay


class Command(BaseCommand):
    args = '<path to shapefile>'
    help = _('Load locations')

    def handle(self, *args, **options):
        location_code = settings.MSPRAY_LOCATION_FIELD
        count = 0

        for spraypoint in SprayDay.objects.iterator():
            code = spraypoint.data.get(location_code)
            if code:
                location = Location.objects.get(code=code)
                spraypoint.location = location
                spraypoint.save()
                count += 1

        print("Updated {} spraypoints".format(count))
