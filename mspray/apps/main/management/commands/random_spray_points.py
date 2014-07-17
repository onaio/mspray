import random

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import TargetArea, Household, SprayDay


def get_split(total, val1, val2, val3):
    val1 = int(round(((val1/100) * total)))
    val2 = int(round(((val2/100) * total)))
    val3 = total

    return {1: val1, 2: val2, 3: val3}


class Command(BaseCommand):
    help = _('Create random spray points for testing')

    def handle(self, *args, **options):
        for target in TargetArea.objects.all():
            random_households = Household.objects.filter(
                geom__coveredby=target.geom).order_by('?')

            count = random_households.count()
            sprayed_num = int((random.uniform(4, 9) / 10) * count)
            random_households = random_households[:sprayed_num]

            random_ranges = [(10, 50, 40), (20, 30, 50), (30, 40, 30)]
            choice = random.randint(1, 3)
            random_range = random_ranges[choice - 1]
            start = 0
            split = get_split(sprayed_num, *random_range)
            end = sprayed_num

            for day in range(1, 4):
                end = split[day] if start != end else sprayed_num

                for h in random_households[start: end]:
                    SprayDay.objects.create(day=day, geom=h.geom.pop())
                start = split[day]