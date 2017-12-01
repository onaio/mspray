from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.utils import find_missing_performance_report_records
from mspray.apps.main.utils import performance_report


class Command(BaseCommand):
    help = _('Sync missing performance report data')

    def handle(self, *args, **options):
        missing_sprayformids = find_missing_performance_report_records()

        queryset = SprayDay.objects.filter(
            data__sprayformid__in=missing_sprayformids).distinct(
            'spray_operator')

        for q in queryset.objects.all():
            performance_report(q.spray_operator)
