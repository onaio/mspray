from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.translation import gettext as _

from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.models.district import District


class Command(BaseCommand):
    help = _('Load districts from TargetArea Model')

    def handle(self, *args, **options):
        qs = TargetArea.objects.filter(targeted=TargetArea.TARGETED_VALUE)\
            .values('district_name').distinct()\
            .annotate(num_houses=Sum('houses'))

        for d in qs:
            geom = TargetArea.objects\
                .filter(district_name=d['district_name'],
                        targeted=TargetArea.TARGETED_VALUE)\
                .collect()
            District.objects.create(
                district_name=d['district_name'],
                houses=d['num_houses'],
                geom=geom
            )
            print(d['district_name'], d['num_houses'], geom.num_points)
