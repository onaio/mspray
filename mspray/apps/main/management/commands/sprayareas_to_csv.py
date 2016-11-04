import codecs
import csv

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location
from mspray.apps.main.views.home import _data
from mspray.apps.main.utils import get_location_qs


class Command(BaseCommand):
    help = _('Create unique spraypoint data points')

    def handle(self, *args, **options):
        count = 0
        qs = get_location_qs(Location.objects.filter(level='ta'))
        qs = qs.extra(select={
            "xmin": 'ST_xMin("main_location"."geom")',
            "ymin": 'ST_yMin("main_location"."geom")',
            "xmax": 'ST_xMax("main_location"."geom")',
            "ymax": 'ST_yMax("main_location"."geom")'
        }).values(
            'pk', 'code', 'level', 'name', 'parent', 'structures',
            'xmin', 'ymin', 'xmax', 'ymax', 'num_of_spray_areas',
            'num_new_structures', 'total_structures', 'parent__name',
            'parent__parent__name', 'parent__parent__pk', 'parent__pk'
        ).order_by('parent__parent__name', 'parent__name', 'name')

        with codecs.open('/tmp/all_sprayareas.csv', 'w',
                         encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            for row in _data(qs, {}):
                writer.writerow(row)
                count += 1
                if count % 100 == 0:
                    self.stdout.write('Written: %d records' % count)

        self.stdout.write('Finished: %d records' % count)
