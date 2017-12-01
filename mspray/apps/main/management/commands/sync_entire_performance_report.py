from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayOperator
from mspray.apps.main.utils import performance_report


class Command(BaseCommand):
    help = _('Sync entire performance report afresh')

    def handle(self, *args, **options):
        for sop in SprayOperator.objects.all():
            performance_report(sop)
