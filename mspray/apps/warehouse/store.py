import os
import time
from datetime import timedelta

from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer
from mspray.apps.warehouse.ingest import ingest_sprayday


sprayday_dir_path = getattr(settings, 'SPRAYDAY_DRUID_DATA_DIRECTORY',
                            'sprayday/')


def get_intervals(queryset):
    """
    Gets intervals from Queryset to be used by Druid ingestion
    """
    queryset = queryset.order_by('created_on')
    first = queryset.first().data['_submission_time']
    last = queryset.last().data['_submission_time']
    return "{}/{}".format(first, last)


def get_queryset(minutes):
    """
    Returns a queryset of objects created x minutes ago
    """
    x_minutes_ago = timezone.now() - timedelta(minutes=minutes)
    queryset = SprayDay.objects.filter(
                    created_on__gte=x_minutes_ago).order_by('created_on')
    return queryset


def get_data(minutes=10):
    """
    Gets data submitted in the last x minutes and stores it
    returns filename
    """
    queryset = get_queryset(minutes)
    # get intervals
    first = queryset.first().data['_submission_time']
    last = queryset.last().data['_submission_time']
    intervals = get_intervals(queryset)
    filename = "{}/minutes".format(settings.DRUID_SPRAYDAY_DATASOURCE) + \
        "/sprayday-{}-{}.json".format(first, last)

    path = create_sprayday_druid_json_file(queryset=queryset,
                                           filename=filename)
    url = settings.AWS_S3_BASE_URL + path
    return ingest_sprayday(url, intervals=intervals)


def get_historical_data(day=None, month=None, year=None):
    """
    Gets and stores data based on one or all of day, month and year
    returns filename
    """
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
            intervals = get_intervals(queryset)
            path = create_sprayday_druid_json_file(queryset=queryset,
                                                   filename=filename)
            url = settings.AWS_S3_BASE_URL + path
            return ingest_sprayday(url, intervals=intervals)


def create_sprayday_druid_json_file(queryset=None, filename=None,
                                    path=sprayday_dir_path):
    """
    Takes a queryset and creates a json file containing druid-ready data
    returns the filename
    """
    from mspray.apps.main.utils import queryset_iterator  # noqa

    if not queryset:
        queryset = SprayDay.objects.all().order_by('spray_date')

    if filename is None:
        epoch = int(time.time())
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
