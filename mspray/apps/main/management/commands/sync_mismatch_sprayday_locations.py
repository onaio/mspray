import gc

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.utils import get_spraydays_with_mismatched_locations
from mspray.apps.main.utils import queryset_iterator
from mspray.apps.main.tasks import link_spraypoint_with_osm


class Command(BaseCommand):
    help = _('Find SprayDay objects with mismatched locations and re-link '
             'with OSM data')

    def handle(self, *args, **options):
        queryset = get_spraydays_with_mismatched_locations()
        print("{} mismatched records".format(queryset.count()))
        for record in queryset_iterator(queryset):
            print("SprayDay ID: {} ".format(record.pk))
            link_spraypoint_with_osm.delay(record.pk)
            gc.collect()
