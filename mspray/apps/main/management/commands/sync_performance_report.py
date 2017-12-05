from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.utils import find_missing_performance_report_records
from mspray.apps.main.utils import performance_report
from mspray.apps.main.utils import queryset_iterator


class Command(BaseCommand):
    help = _('Sync missing performance report data')

    def handle(self, *args, **options):
        missing_sprayformids = find_missing_performance_report_records()

        queryset = SprayDay.objects.filter(
            data__sprayformid__in=missing_sprayformids).distinct(
            'spray_operator')

        for record in queryset_iterator(queryset):
            performance_report(record.spray_operator)
