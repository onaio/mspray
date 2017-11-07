import os
import time

from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer
from mspray.apps.main.utils import queryset_iterator


sprayday_dir_path = getattr(settings, 'SPRAYDAY_DRUID_DATA_DIRECTORY',
                            'sprayday/')


def get_historical_data(day=None, month=None, year=None):
    if any([year, month, day]):
        path = "/".join([str(x) for x in [year, month, day] if x is not None])
        filename = "{}/".format(settings.DRUID_SPRAYDAY_DATASOURCE) + path +\
            "/sprayday.json"
        queryset = SprayDay.objects.all()
        if day:
            queryset = queryset.filter(spray_date__day=day)
        if month:
            queryset = queryset.filter(spray_date__month=month)
        if year:
            queryset = queryset.filter(spray_date__year=year)
        if queryset:
            return create_sprayday_druid_json_file(queryset=queryset,
                                                   filename=filename)


def create_sprayday_druid_json_file(queryset=None, filename=None,
                                    path=sprayday_dir_path):
    if not queryset:
        queryset = SprayDay.objects.all().order_by('spray_date')
    epoch = int(time.time())
    if filename is None:
        filename = "{}sprayday_{}.json".format(path, epoch)
    if isinstance(default_storage, FileSystemStorage):
        filename = os.path.join(default_storage.base_location, filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    lines = []
    for record in queryset_iterator(queryset, 1000):
        data = SprayDayDruidSerializer(record).data
        line = JSONRenderer().render(data)
        lines.append(line)
    content = b'\n'.join(lines)
    file = default_storage.open(filename, "wb")
    file.write(content)
    file.close()
    return filename
