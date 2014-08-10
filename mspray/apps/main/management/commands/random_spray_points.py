import datetime
import json
import os
import random

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.utils.translation import gettext as _

from mspray.apps.main.models import TargetArea, Household, SprayDay
from mspray.apps.main import tests
from mspray.apps.main.utils import add_spray_data


def get_split(total, val1, val2, val3):
    val1 = int(round(((val1/100) * total)))
    val2 = int(round(((val2/100) * total)))
    val3 = total

    return {1: val1, 2: val2, 3: val3}


def _load_json_file(filename):
    data = None
    path = os.path.join(
        os.path.dirname(tests.__file__),
        'fixtures', filename)

    with open(path) as f:
        data = json.load(f)

    return data


class Command(BaseCommand):
    help = _('Create random spray points for testing')
    _submission_data = None
    _no_submission_data = None
    yes_no_list = ['yes', 'no', 'yes', 'yes', 'yes', 'no', 'yes', 'yes']

    def _get_submission_data_yes(self):
        if self._submission_data is not None:
            return self._submission_data

        fn = '88037_submission.json'
        self._submission_data = _load_json_file(fn)

        return self._submission_data

    def _get_submission_data_no(self):
        if self._no_submission_data is not None:
            return self._no_submission_data

        fn = '88039_submission.json'
        self._no_submission_data = _load_json_file(fn)

        return self._no_submission_data

    def _add_sprayday(self, day, geom, submission_id):
        choice = random.choice(self.yes_no_list)

        if choice == 'yes':
            data = self._get_submission_data_yes()
        else:
            data = self._get_submission_data_no()
            data['unsprayed/reason'] = random.choice(['1', '2', '3', '4', '5'])

        geolocation = "%s %s" % (geom.x, geom.y)
        data['structure_gps'] = geolocation
        data['date'] = "%s" % day
        data['_id'] = submission_id
        data['sprayed/was_sprayed'] = choice
        add_spray_data(data)

    def handle(self, *args, **options):
        k = 1

        SprayDay.objects.all().delete()

        for target in TargetArea.objects.all():
            random_households = Household.objects.filter(
                geom__coveredby=target.geom).order_by('?')
            count = random_households.count()

            query = "SELECT id, RandomPoint(bgeom) as rp FROM main_household"\
                " WHERE ST_CoveredBy(geom, ST_GeomFromText('SRID=4326;%s'))"\
                " ORDER BY RANDOM()" % target.geom
            random_households = Household.objects.raw(query)
            sprayed_num = int((random.uniform(4, 9) / 10) * count)
            random_households = random_households[:sprayed_num]

            random_ranges = [(10, 50, 40), (20, 30, 50), (30, 40, 30)]
            choice = random.randint(1, 3)
            random_range = random_ranges[choice - 1]
            start = 0
            split = get_split(sprayed_num, *random_range)
            end = sprayed_num
            dates = [datetime.date(2014, 8, d) for d in range(1, 4)]
            used = []
            for day in dates:
                end = split[day.day] if start != end else sprayed_num

                for h in random_households[start: end]:
                    geom = GEOSGeometry(h.rp)

                    if geom in used:
                        continue
                    else:
                        used.append(geom)

                    self._add_sprayday(day, geom, k)
                    k += 1
                start = split[day.day]
