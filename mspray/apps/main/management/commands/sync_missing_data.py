from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from mspray.apps.main.ona import fetch_form_data
from mspray.apps.main.utils import add_spray_data
from mspray.apps.main.models import SprayDay

FORMID = getattr(settings, 'ONA_FORM_PK', 0)


class Command(BaseCommand):
    help = _('Fetch data from ona server.')

    def add_arguments(self, parser):
        parser.add_argument('--formid', dest='formid', default=FORMID,
                            type=int, help='form id')

    def handle(self, *args, **options):
        formid = int(options['formid']) if 'formid' in options else FORMID

        if formid != 0:
            old_data = SprayDay.objects.filter().order_by('-submission_id')\
                .values_list('submission_id', flat=True)
            raw_data = fetch_form_data(formid, dataids_only=True)
            all_data = [rec['_id'] for rec in raw_data]
            if all_data is not None and isinstance(all_data, list):
                new_data = list(set(all_data) - set(old_data))
                count = len(new_data)
                counter = 0
                self.stdout.write(
                    "Need to pull {} records from Ona.".format(count)
                )
                for dataid in new_data:
                    counter += 1
                    self.stdout.write(
                        "Pulling {} of {}".format(counter, count)
                    )
                    rec = fetch_form_data(formid, dataid=dataid)
                    if isinstance(rec, dict):
                        try:
                            add_spray_data(rec)
                        except IntegrityError:
                            continue
