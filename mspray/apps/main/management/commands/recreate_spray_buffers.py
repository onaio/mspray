from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.libs.utils.geom_buffer import with_metric_buffer

BUFFER_SIZE = getattr(settings, 'MSPRAY_NEW_BUFFER_WIDTH', 4)  # default to 4m

FORMID = getattr(settings, 'ONA_FORM_PK', 0)


class Command(BaseCommand):
    help = _('Update sprayed buffers.')

    def handle(self, *args, **options):
        new_structures = SprayDay.objects.filter(
            Q(data__has_key='osmstructure:node:id') |
            Q(data__has_key='newstructure/gps'),
            geom__isnull=False
        )
        count = int(new_structures.count())

        for i in new_structures:
            i.bgeom = with_metric_buffer(i.geom, BUFFER_SIZE)
            i.save()

        self.stdout.write("Updated %d structures" % count)
