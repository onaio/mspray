from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.ona import fetch_form_data
from mspray.apps.main.utils import add_spray_operator_daily
from mspray.apps.main.models import SprayOperatorDailySummary

FORMID = getattr(settings, 'ONA_FORM_PK', 0)


class Command(BaseCommand):
    help = _('Fetch data from ona server.')

    def add_arguments(self, parser):
        parser.add_argument('--formid', dest='formid', default=FORMID,
                            type=int, help='form id')

    def handle(self, *args, **options):
        formid = 141280
        latest = SprayOperatorDailySummary.objects.filter().order_by(
            'submission_id'
        ).values_list(
            'submission_id', flat=True
        ).first()
        data = fetch_form_data(formid, latest)
        for a in data:
            add_spray_operator_daily(a)
        print("successfully imported data")
