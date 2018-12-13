"""utils module for reveal app"""
import json

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.db.models.functions import Coalesce

from dateutil import parser

from mspray.apps.main.models import Household, Location, SprayDay, SprayPoint
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

    if spray_status == settings.REVEAL_NOT_VISITED_VALUE:
        # stop here because we have no spray data!
        return None

    try:
        submission_id = int(submission_id)
    except ValueError:
        # means we are not dealing with a numeric value
        # we need to generate an int submission_id
        id_name = f'data__{settings.REVEAL_DATA_ID_FIELD}'
        try:
            # try use an existing id in the case that we have already received
            # this spray data before
            existing = SprayDay.objects.get(**{id_name: submission_id})
        except SprayDay.DoesNotExist:
            # generate a new id by incrementing the last one we received
            last = SprayDay.objects.all().aggregate(
                last_id=Coalesce(Max('submission_id'), 0))
            submission_id = last['last_id'] + 1
        else:
            submission_id = existing.submission_id

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
            sprayday.osmid = household.hh_id
            location = sprayday.location = household.location
            sprayday.save()

            if spray_status == settings.REVEAL_NOT_VISITED_VALUE:
                household.visited = False
            else:
                household.visited = True

            household.sprayable = sprayday.sprayable
            household.save()

            SprayPoint.objects.update_or_create(
                sprayday=sprayday,
                defaults={
                    "data_id": sprayday.data[settings.REVEAL_DATA_ID_FIELD],
                    "location": sprayday.location
                }
            )

        return sprayday
