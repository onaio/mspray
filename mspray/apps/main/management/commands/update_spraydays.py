from django.utils.dateparse import parse_datetime
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay


class Command(BaseCommand):
    help = _('Create unique spraypoint data points')

    def handle(self, *args, **options):
        for sprayday in SprayDay.objects.iterator():
            start_time = sprayday.data.get('start')
            end_time = sprayday.data.get('end')
            if start_time:
                start_time = parse_datetime(start_time)
                sprayday.start_time = start_time

            if end_time:
                end_time = parse_datetime(end_time)
                sprayday.end_time = end_time

            if end_time or start_time:
                sprayday.save()
