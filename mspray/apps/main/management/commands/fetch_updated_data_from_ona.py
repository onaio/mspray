from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from mspray.apps.main.ona import fetch_form_data
from mspray.apps.main.utils import add_spray_data
from mspray.apps.main.models import SprayDay

FORMID = getattr(settings, 'ONA_FORM_PK', 0)


class Command(BaseCommand):
    help = _('Fetch edited data from ona server.')

    def add_arguments(self, parser):
        parser.add_argument('--formid', dest='formid', default=FORMID,
                            type=int, help='form id')

    def handle(self, *args, **options):
        formid = int(options['formid']) if 'formid' in options else FORMID

        if formid != 0:
            data = fetch_form_data(formid, edited_only=True)
            if data is not None and isinstance(data, list):
                for rec in data:
                    try:
                        add_spray_data(rec)
                    except IntegrityError:
                        continue
