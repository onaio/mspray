import time

from django.conf import settings

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.models import Household, SprayDay
from mspray.apps.warehouse.serializers import HouseHoldDruidSerializer
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer
from mspray.apps.main.utils import queryset_iterator


household_dir_path = getattr(settings, 'HOUSEHOLD_DRUID_DATA_DIRECTORY',
                             '/tmp/household/')
sprayday_dir_path = getattr(settings, 'SPRAYDAY_DRUID_DATA_DIRECTORY',
                            '/tmp/sprayday/')


def create_household_druid_json_files(queryset=None, path=household_dir_path):
    if not queryset:
        queryset = Household.objects.all().order_by('id')
    epoch = int(time.time())
    filename = "{}household_{}.json".format(path, epoch)
    for household in queryset_iterator(queryset, 1000):
        data = HouseHoldDruidSerializer(household).data
        line = JSONRenderer().render(data)
        with open(filename, "ab") as f:
            f.write(line + b'\n')


def create_sprayday_druid_json_files(queryset=None, path=sprayday_dir_path):
    if not queryset:
        queryset = SprayDay.objects.all().order_by('spray_date')
    epoch = int(time.time())
    filename = "{}sprayday_{}.json".format(path, epoch)
    for record in queryset_iterator(queryset, 1000):
        data = SprayDayDruidSerializer(record).data
        line = JSONRenderer().render(data)
        with open(filename, "ab") as f:
            f.write(line + b'\n')
