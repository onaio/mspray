from __future__ import absolute_import

from django.conf import settings

from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay
from mspray.apps.main.ona import fetch_osm_xml
from mspray.apps.main.osm import parse_osm_ways
from mspray.apps.main.osm import parse_osm_nodes
from mspray.celery import app

HAS_UNIQUE_FIELD = getattr(settings, 'MSPRAY_UNIQUE_FIELD', None)


def get_location_from_data(data):
    district = data.get('district')
    target_area = data.get('target_area')
    location = None
    try:
        location = Location.objects.get(name=target_area,
                                        parent__code=district)
    except Location.DoesNotExist:
        pass

    return location


def get_location_from_osm(data):
    geom = None
    is_node = False
    location = None
    osm_xml = fetch_osm_xml(data)
    osmstructure = data.get('osmstructure')
    if osm_xml is not None:
        geoms = []
        is_node = osmstructure and osmstructure.startswith('OSMNode')
        if is_node:
            geoms = parse_osm_nodes(osm_xml)
        else:
            geoms = parse_osm_ways(osm_xml)
        if len(geoms):
            geom = geoms[0]
            locations = Location.objects.filter(
                geom__covers=geom.centroid if not is_node else geom,
                level=settings.MSPRAY_TA_LEVEL
            )
            if locations:
                location = locations.first()

    return location, geom, is_node


def set_spraypoint_location(sp, location, geom, is_node=False):
    from mspray.apps.main.utils import add_unique_data
    if geom:
        sp.geom = geom.centroid if not is_node else geom
        sp.bgeom = geom if not is_node else sp.geom.buffer(0.00004, 1)

    if location:
        sp.location = location
        sp.save()

        unique_field = HAS_UNIQUE_FIELD
        if unique_field:
            add_unique_data(sp, unique_field, location)


@app.task
def link_spraypoint_with_osm(pk):
    try:
        sp = SprayDay.objects.get(pk=pk)
    except SprayDay.DoesNotExist:
        pass
    else:
        location, geom, is_node = get_location_from_osm(sp.data)
        if location is None:
            location = get_location_from_data(sp.data)
        set_spraypoint_location(sp, location, geom, is_node)

        return sp.pk
