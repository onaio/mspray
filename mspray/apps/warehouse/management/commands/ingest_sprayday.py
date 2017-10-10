from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.warehouse.ingest import ingest_sprayday


class Command(BaseCommand):
    help = _('Send command to Druid to ingest SprayDay data')

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        path = options['path']
        ingest_sprayday(path)
