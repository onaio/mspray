from mspray.celery import app
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.stream import send_to_tranquility


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
