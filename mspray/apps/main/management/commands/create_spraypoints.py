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

        for sprayday in SprayDay.objects.iterator():
            add_unique_data(sprayday, unique_field)

        self.stdout.write("{} unique data points of {}.".format(
            SprayPoint.objects.count(), SprayDay.objects.count()
        ))
