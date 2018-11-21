"""utils module for reveal app"""
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError

from mspray.apps.main.models.location import Location
from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.utils import geojson_from_gps_string
from mspray.apps.reveal.common_tags import NOT_PROVIDED


def add_spray_data(data: dict):
    """"
    Add spray data submission from reveal
    """
    submission_id = data.get(settings.REVEAL_DATA_ID_FIELD)
    spray_date = data.get(settings.REVEAL_DATE_FIELD)

    try:
        spray_date = datetime.strptime(spray_date, "%Y-%m-%d")
    except TypeError:
        raise ValidationError(f"{settings.REVEAL_DATE_FIELD} {NOT_PROVIDED}")
    else:
        location = None
        gps_field = data.get(settings.REVEAL_GPS_FIELD)

        if gps_field is None:
            raise ValidationError(
                f"{settings.REVEAL_GPS_FIELD} {NOT_PROVIDED}")

        geom = geojson_from_gps_string(gps_field)

        locations = Location.objects.filter(
            geom__contains=geom, level=settings.MSPRAY_TA_LEVEL
        )
        if locations:
            location = locations[0]

        sprayday, _ = SprayDay.objects.get_or_create(
            submission_id=submission_id, spray_date=spray_date
        )
        sprayday.data = data
        sprayday.save()

        if geom is not None:
            sprayday.geom = geom
        if location is not None:
            sprayday.location = location

        sprayday.save()

        return sprayday
