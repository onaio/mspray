from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay


class Command(BaseCommand):
    help = _('Set location based on target area field in data')

    def handle(self, *args, **options):
        def update_mismatched(was_sprayed, status):
            mismatched = SprayDay.objects.filter(was_sprayed=was_sprayed)\
                .extra(
                    where=['(data->>%s) != %s'],
                    params=[settings.MSPRAY_WAS_SPRAYED_FIELD, status]
                )
            count = int(mismatched.count())
            mismatched.update(was_sprayed=was_sprayed is not True)

            return count

        print("SPRAYED FIELD: {}".format(settings.MSPRAY_WAS_SPRAYED_FIELD))
        print("SPRAYED VALUE: {}".format(settings.MSPRAY_WAS_SPRAYED_VALUE))
        print("NOT SPRAYED VALUE: {}".format(
            settings.MSPRAY_WAS_NOT_SPRAYED_VALUE))

        true_mismatch = int(update_mismatched(
            True, settings.MSPRAY_WAS_SPRAYED_VALUE))
        false_mismatch = int(update_mismatched(
            False, settings.MSPRAY_WAS_NOT_SPRAYED_VALUE))

        self.stdout.write(
            "Mismatched to True: %s. Mismatched to False: %s." % (
                true_mismatch, false_mismatch
            )
        )
