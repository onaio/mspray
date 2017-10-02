from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import SprayPoint
from mspray.apps.main.utils import add_unique_data


class Command(BaseCommand):
    help = _('Create unique spraypoint data points')

    def handle(self, *args, **options):
        unique_field = getattr(settings, 'MSPRAY_UNIQUE_FIELD')
        if not unique_field:
            settings.stderr.write('MSPRAY_UNIQUE_FIELD is not defined')
            return
        pre_count = SprayDay.objects.exclude(location=None).count()
        count = 0

        for sprayday in SprayDay.objects.exclude(location=None).iterator():
            add_unique_data(sprayday, unique_field, sprayday.location)
            count += 1
            if count % 1000 == 0:
                self.stdout.write("handling {} of {}".format(count, pre_count))

        self.stdout.write("{} unique data points of {}.".format(
            SprayPoint.objects.count(), pre_count
        ))
