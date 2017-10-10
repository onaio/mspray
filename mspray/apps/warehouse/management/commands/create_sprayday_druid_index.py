from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.warehouse.store import create_sprayday_druid_json_files


class Command(BaseCommand):
    help = _('Create Druid index file for SprayDay objects')

    def handle(self, *args, **options):
        create_sprayday_druid_json_files()
