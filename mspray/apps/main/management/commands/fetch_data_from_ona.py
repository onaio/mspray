from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _

from mspray.libs.ona import fetch_form_data
from mspray.apps.main.utils import add_spray_data
from mspray.apps.main.models import SprayDay

FORMID = getattr(settings, "ONA_FORM_PK", 0)


class Command(BaseCommand):
    help = _("Fetch data from ona server.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--formid", dest="formid", default=FORMID, type=int, help="form id"
        )

    def handle(self, *args, **options):
        formid = int(options["formid"]) if "formid" in options else FORMID

        if formid != 0:
            latest = (
                SprayDay.objects.filter()
                .order_by("-submission_id")
                .values_list("submission_id", flat=True)
                .first()
            )
            data = fetch_form_data(formid, latest)
            if data is not None and isinstance(data, list):
                for rec in data:
                    if SprayDay.objects.filter(
                        submission_id=rec.get("_id")
                    ).count():
                        continue
                    try:
                        add_spray_data(rec)
                    except IntegrityError:
                        continue
