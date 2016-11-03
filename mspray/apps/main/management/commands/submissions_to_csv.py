import codecs
import csv

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.views.sprayday import _data


class Command(BaseCommand):
    help = _('Create unique spraypoint data points')

    def handle(self, *args, **options):
        count = 0
        qs = SprayDay.objects.select_related('location__parent__parent')
        with codecs.open('/tmp/all_submissions.csv', 'w',
                         encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            for row in _data(qs):
                writer.writerow(row)
                count += 1
                if count % 5000 == 0:
                    self.stdout.write('Written: %d records' % count)
        self.stdout.write('Finished: %d records' % count)
