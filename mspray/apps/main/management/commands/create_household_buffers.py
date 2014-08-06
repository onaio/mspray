from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main import utils
from mspray.apps.main.models.households_buffer import HouseholdsBuffer


class Command(BaseCommand):
    help = _('Create Household buffers.')
    option_list = BaseCommand.option_list + (
        make_option('-d', '--distance',
                    default=0.00009, dest='distance', type=float),
        make_option('-f', '--force', default=False,
                    dest='recreate')
    )

    def handle(self, *args, **options):
        distance = options.get('distance')
        recreate = options.get('recreate')
        count = HouseholdsBuffer.objects.count()

        utils.create_households_buffer(distance=distance, recreate=recreate)

        after_count = HouseholdsBuffer.objects.count()

        print("before: %d Buffers" % count)
        print("after: %d Buffers" % after_count)
