import time

from django.conf import settings

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.models import Household, SprayDay
from mspray.apps.warehouse.serializers import HouseHoldDruidSerializer
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer
from mspray.apps.warehouse.utils import chunked_iterator


household_dir_path = getattr(settings, 'HOUSEHOLD_DRUID_DATA_DIRECTORY',
                             '/tmp/household/')
sprayday_dir_path = getattr(settings, 'SPRAYDAY_DRUID_DATA_DIRECTORY',
                            '/tmp/sprayday/')


def create_household_druid_json_files(queryset=None, path=household_dir_path):
    if not queryset:
        queryset = Household.objects.all().order_by('id')
    epoch = int(time.time())
    for households in chunked_iterator(queryset, 1000):
        data = HouseHoldDruidSerializer(households, many=True).data
        lines = [JSONRenderer().render(dd) for dd in data]
        filename = "{}household_{}.json".format(path, epoch)
        with open(filename, "ab") as f:
            f.write(b'\n'.join(lines))


def create_sprayday_druid_json_files(queryset=None, path=sprayday_dir_path):
    if not queryset:
        queryset = SprayDay.objects.all().order_by('spray_date')
    epoch = int(time.time())
    for records in chunked_iterator(queryset, 1000):
        data = SprayDayDruidSerializer(records, many=True).data
        lines = [JSONRenderer().render(dd) for dd in data]
        filename = "{}sprayday_{}.json".format(path, epoch)
        with open(filename, "ab") as f:
            f.write(b'\n'.join(lines))
