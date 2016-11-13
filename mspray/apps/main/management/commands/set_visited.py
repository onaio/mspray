from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.tasks import set_district_sprayed_visited


class Command(BaseCommand):
    help = _('Set num spray areas of visited location')

    def handle(self, *args, **options):
        set_district_sprayed_visited()
