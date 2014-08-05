from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main import utils


class Command(BaseCommand):
    help = _('Create Household buffers.')

    def handle(self, *args, **options):
        utils.create_households_buffer()
