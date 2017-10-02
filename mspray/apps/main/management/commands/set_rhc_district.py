from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.utils import queryset_iterator


class Command(BaseCommand):
    help = _('Set location based on target area field in data')

    def handle(self, *args, **options):
        qs = SprayDay.objects.filter(
            Q(rhc__isnull=True) | Q(district__isnull=True),
            location__isnull=False
        ).order_by('id')

        self.stdout.write("Starting to process: %d" % qs.count())
        for sp in queryset_iterator(qs):
            sp.rhc = sp.location.parent
            sp.district = sp.location.parent.parent
            sp.save()

        self.stdout.write("Failed to process: %d" % qs.count())
