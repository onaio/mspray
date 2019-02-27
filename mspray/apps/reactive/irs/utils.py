"""Utils module"""
from django.conf import settings
from django.contrib.gis.geos import MultiPolygon

from mspray.apps.main.models import Location


def get_chw_location(chw: object):
    """
    Gets or creates a Community Health Worker location

    :param chw: Community Health Worker object
    :return: Location object linked to the Community Health Worker
    """

    level = settings.MSPRAY_REACTIVE_IRS_CHW_LOCATION_LEVEL

    if level == settings.MSPRAY_DISTRICT_LEVEL:
        parent = None
    else:
        parent = Location.objects.filter(
            geom__contains=chw.geom,
            level=settings.MSPRAY_REACTIVE_IRS_CHW_LOCATION_PARENT_LEVEL,
        ).first()

    location, _ = Location.objects.update_or_create(
        code=f"{settings.MSPRAY_REACTIVE_IRS_CHW_CODE_PREFIX}{chw.pk}",
        defaults={
            "name": chw.name,
            "level": level,
            "geom": MultiPolygon([chw.bgeom]),
            "parent": parent,
        },
    )

    return location
