from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.utils import find_mismatched_spraydays


class Command(BaseCommand):
    help = _('Set location based on target area field in data')

    def handle(self, *args, **options):

        print("SPRAYED FIELD: {}".format(settings.MSPRAY_WAS_SPRAYED_FIELD))
        print("SPRAYED VALUE: {}".format(settings.MSPRAY_WAS_SPRAYED_VALUE))

        true_mismatch = find_mismatched_spraydays(was_sprayed=True)
        true_mismatch_count = true_mismatch.count()
        true_mismatch.update(was_sprayed=False)

        false_mismatch = find_mismatched_spraydays(was_sprayed=False)
        false_mismatch_count = false_mismatch.count()
        false_mismatch.update(was_sprayed=True)

        self.stdout.write(
            "Mismatched to True: %s. Mismatched to False: %s." % (
                true_mismatch_count, false_mismatch_count
            )
        )
