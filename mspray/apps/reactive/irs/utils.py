"""Utils module"""
from django.conf import settings
from django.contrib.gis.geos import MultiPolygon

from mspray.apps.main.models import Location
from mspray.apps.reactive.irs.models import CommunityHealthWorker


def create_chw_object_from_location(location: object):
    """Creates a Community Health Worker object from a location object

    Arguments:
        location {object} -- Location object

    Returns:
        object -- Community Health Worker object
    """
    chw = CommunityHealthWorker.objects.filter(location=location).first()
    if chw:
        return chw

    try:
        chw = CommunityHealthWorker.objects.get(code=location.code)
    except CommunityHealthWorker.DoesNotExist:
        chw = CommunityHealthWorker(
            name=location.name,
            location=location,
            code=location.code,
            geom=location.geom.centroid,
            bgeom=location.geom,
        )
    else:
        chw.location = location

    chw.save()
    return chw


def get_chw_location(chw: object):
    """
    Gets or creates a Community Health Worker location

    :param chw: Community Health Worker object
    :return: Location object linked to the Community Health Worker
    """
    if not chw.location:
        level = getattr(settings, "MSPRAY_REACTIVE_IRS_CHW_LOCATION_LEVEL",
                        "chw")
        code_pre = getattr(settings, "MSPRAY_REACTIVE_IRS_CHW_CODE_PREFIX",
                           "CHW_")

        if level == settings.MSPRAY_DISTRICT_LEVEL:
            parent = None
        else:
            parent = Location.objects.filter(
                geom__contains=chw.geom,
                level=settings.MSPRAY_REACTIVE_IRS_CHW_LOCATION_PARENT_LEVEL,
            ).first()

        location, _ = Location.objects.update_or_create(
            code=f"{code_pre}{chw.code}",
            defaults={
                "name": chw.name,
                "level": level,
                "geom": MultiPolygon([chw.bgeom]),
                "parent": parent,
            },
        )

        return location

    return chw.location
