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
            district = spraypoint.data.get('district')
            if code:
                try:
                    location = Location.objects.get(
                        name=code.replace('_', ' / '),
                        parent__code=district
                    )
                except Location.DoesNotExist:
                    pass
                else:
                    if spraypoint.location is None or \
                            (location != spraypoint.location and
                             location.parent != spraypoint.location.parent):
                        if spraypoint.location is not None:
                            self.stdout.write('{}:{} {} to {} {}'.format(
                                spraypoint.pk, spraypoint.location.name,
                                spraypoint.location.parent.name, location.name,
                                location.parent.name
                            ))
                        spraypoint.location = location
                        spraypoint.save()
                        count += 1

        self.stdout.write("Updated {} spraypoints".format(count))
