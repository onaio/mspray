from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.utils import remove_household_overlapping_duplicates


class Command(BaseCommand):
    help = _("Remove duplicate Household objects that are overlapping")

    def handle(self, *args, **options):
        remove_household_overlapping_duplicates()
