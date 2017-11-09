from datetime import timedelta

from django.utils import timezone

from mspray.celery import app
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.stream import send_to_tranquility
from mspray.apps.warehouse.store import get_data, get_historical_data


@app.task
def stream_to_druid(spray_day_obj_id):
    """
    Sends a SprayDay object to tranquility for ingestion into Druid
    """

    try:
        spray_day_obj = SprayDay.objects.get(pk=spray_day_obj_id)
    except SprayDay.DoesNotExist:
        pass
    else:
        send_to_tranquility(spray_day_obj)


@app.task
def reload_druid_data(minutes=10):
    """
    Refreshes Druid data for records created in the last x minutes
    """
    get_data(minutes=minutes)


@app.task
def reload_yesterday_druid_data():
    """
    Refreshes druid data for records created the day before today
    Ideally should be set up as a periodic task that runs at 12:01am
    """
    today = timezone.now()
    yesterday = today - timedelta(days=1)
    get_historical_data(day=yesterday.day, month=yesterday.month,
                        year=yesterday.year)
