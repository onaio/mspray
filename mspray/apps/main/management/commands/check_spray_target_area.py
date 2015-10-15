from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import Location


class Command(BaseCommand):
    help = _('Set location based on target area field in data')

    def handle(self, *args, **options):
        count = 0
        final_count = SprayDay.objects.count()
        for sprayday in SprayDay.objects.select_related().iterator():
            ta = sprayday.data.get('target_area')
            if ta == 'NM' or sprayday.location is None:
                final_count -= 1
                continue
            try:
                location = Location.objects.get(name=ta.replace('_', ' / '))
                if location != sprayday.location:
                    count += 1
                    self.stdout.write("{}: {} != {}, {}".format(
                        sprayday.pk, location, sprayday.location,
                        sprayday.data.get('osmstructure')
                    ))
            except Location.DoesNotExist:
                pass

        self.stdout.write(
            "{} points of {} did not have matching location.".format(
                count, final_count
            )
        )
