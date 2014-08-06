from optparse import make_option
from django.db import connection

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main import utils
from mspray.apps.main.models.households_buffer import HouseholdsBuffer


class Command(BaseCommand):
    help = _('Create Household buffers.')
    option_list = BaseCommand.option_list + (
        make_option('-d', '--distance',
                    default=15, dest='distance', type=float),
        make_option('-f', '--force', default=False,
                    dest='recreate')
    )

    def _set_household_buffer(self, distance=15):
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE main_household SET bgeom = ST_GeomFromText(ST_AsText("
            "ST_Buffer(geography(geom), %s)), 4326);" % distance)

    def handle(self, *args, **options):
        distance = options.get('distance')
        recreate = options.get('recreate')
        count = HouseholdsBuffer.objects.count()
        self._set_household_buffer(distance)
        utils.create_households_buffer(recreate=recreate)

        after_count = HouseholdsBuffer.objects.count()

        print("before: %d Buffers" % count)
        print("after: %d Buffers" % after_count)
