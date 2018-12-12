"""utils module for reveal app"""
from django.contrib.gis.geos import GEOSGeometry
import uuid
import json

from dateutil import parser
from django.conf import settings
from django.core.exceptions import ValidationError

from mspray.apps.main.models import Household, Location, SprayDay
from mspray.apps.reveal.common_tags import NOT_PROVIDED


def add_spray_data(data: dict):
    """"
    Add spray data submission from reveal

    Expects:
        submission_id: str => uuid of the submission
        date: str => date of submissions
        location: str => geojson of a Point
        spray_status: str => the spray status
    """
    submission_id = data.get(settings.REVEAL_DATA_ID_FIELD)
    spray_date = data.get(settings.REVEAL_DATE_FIELD)
    spray_status = data.get(settings.REVEAL_SPRAY_STATUS_FIELD)

    # get the int of submission id
    if isinstance(submission_id, str):
        if submission_id.isnumeric():
            submission_id = int(submission_id)
        else:
            try:
                submission_id = uuid.UUID(submission_id).int
            except ValueError:
                raise ValidationError(
                    f"{settings.REVEAL_DATA_ID_FIELD} {NOT_PROVIDED}")

    try:
        spray_date = parser.parse(spray_date)
    except TypeError:
        raise ValidationError(f"{settings.REVEAL_DATE_FIELD} {NOT_PROVIDED}")
    except ValueError:
        raise ValidationError(f"{settings.REVEAL_DATE_FIELD} {NOT_PROVIDED}")
    else:
        spray_date = spray_date.date()

        gps_field = data.get(settings.REVEAL_GPS_FIELD)
        if gps_field is None:
            raise ValidationError(
                f"{settings.REVEAL_GPS_FIELD} {NOT_PROVIDED}")

        if isinstance(gps_field, dict):
            # we need to convert back to geojson
            gps_field = json.dumps(gps_field)

        geom = GEOSGeometry(gps_field)

        # get the location object
        location = Location.objects.filter(
            geom__contains=geom, level=settings.MSPRAY_TA_LEVEL
        ).first()

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

        household = Household.objects.filter(
            bgeom__contains=sprayday.geom).first()

        if household and sprayday.household != household:
            sprayday.household = household
            sprayday.geom = household.geom
            sprayday.bgeom = household.bgeom
            location = sprayday.location = household.location
            sprayday.save()

            if spray_status == settings.REVEAL_NOT_VISITED_VALUE:
                household.visited = False
            else:
                household.visited = True

            household.sprayable = sprayday.sprayable
            household.save()

        return sprayday
