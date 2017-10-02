from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.ona import fetch_form_data
from mspray.apps.main.utils import add_directly_observed_spraying_data
from mspray.apps.main.models import DirectlyObservedSprayingForm


class Command(BaseCommand):
    help = _('Fetch data from ona server.')

    def add_arguments(self, parser):
        parser.add_argument('formid', type=int, help='form id')

    def handle(self, *args, **options):
        formid = int(options['formid'])
        latest = DirectlyObservedSprayingForm.objects.filter().order_by(
            '-submission_id'
        ).values_list(
            'submission_id', flat=True
        ).first()
        data = fetch_form_data(formid, latest)
        pre_count = DirectlyObservedSprayingForm.objects.count()
        for a in data:
            add_directly_observed_spraying_data(a)
        count = DirectlyObservedSprayingForm.objects.count()
        print("successfully imported %d data" % (count - pre_count))
