from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.warehouse.ingest import ingest_household


class Command(BaseCommand):
    help = _('Send command to Druid to ingest Household data')

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        path = options['path']
        ingest_household(path)
