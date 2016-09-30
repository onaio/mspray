from __future__ import absolute_import

import gc
import os

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.utils import IntegrityError

from mspray.apps.main.models import Household
from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay
from mspray.apps.main.models.spray_day import get_osmid
from mspray.apps.main.ona import fetch_form_data
from mspray.apps.main.osm import parse_osm
from mspray.apps.main.ona import fetch_osm_xml
from mspray.apps.main.osm import parse_osm_ways
from mspray.apps.main.osm import parse_osm_nodes
from mspray.apps.main.models.spray_day import STRUCTURE_GPS_FIELD
from mspray.apps.main.models.spray_day import NON_STRUCTURE_GPS_FIELD
from mspray.celery import app

BUFFER_SIZE = getattr(settings, 'MSPRAY_NEW_BUFFER_WIDTH', 0.00007)
HAS_UNIQUE_FIELD = getattr(settings, 'MSPRAY_UNIQUE_FIELD', None)
STRUCTURE_GPS_FIELD = getattr(settings,
                              'MSPRAY_STRUCTURE_GPS_FIELD',
                              STRUCTURE_GPS_FIELD)


def get_new_structure_location(data, geom, is_node=False):
    from mspray.apps.main.utils import geojson_from_gps_string
    if is_node and geom is None:
        gps_field = data.get(STRUCTURE_GPS_FIELD,
                             data.get(NON_STRUCTURE_GPS_FIELD))
        geom = geojson_from_gps_string(gps_field, True) \
            if gps_field is not None else geom
    location = None
    if geom is not None:
        locations = Location.objects.filter(
            geom__contains=geom,
            level=settings.MSPRAY_TA_LEVEL
        )
        if locations:
            location = locations[0]

    return location, geom


def get_location_from_data(data):
    district = data.get('district')
    target_area = data.get('target_area')
    location = None
    try:
        location = Location.objects.get(name=target_area,
                                        parent__code=district)
    except Location.DoesNotExist:
        if target_area == 'NM':
            code = 'NM{}'.format(district)
            location = Location.objects.get(code=code, parent__code=district)

    return location


def get_location_from_osm(data):
    geom = None
    is_node = False
    location = None
    osm_xml = fetch_osm_xml(data)
    if osm_xml is not None:
        geoms = []
        geoms = parse_osm_ways(osm_xml) or parse_osm_nodes(osm_xml)

        if len(geoms):
            geom = geoms[0]['geom']
            is_node = isinstance(geom, Point)
            locations = Location.objects.filter(
                geom__covers=geom,
                level=settings.MSPRAY_TA_LEVEL
            )
            if locations:
                location = locations.first()
        else:
            location = get_location_from_data(data)

    return location, geom, is_node


def set_spraypoint_location(sp, location, geom, is_node=False):
    if geom:
        sp.geom = geom.centroid if not is_node else geom
        sp.bgeom = geom if not is_node else sp.geom.buffer(BUFFER_SIZE)

    if location:
        sp.location = location
        sp.save()

        add_unique_record.delay(sp.pk, location.pk)
    elif geom is not None:
        sp.save()


def get_updated_osm_from_ona(sp):
    formid = getattr(settings, 'ONA_FORM_PK', 0)
    if formid:
        data = fetch_form_data(formid, dataid=sp.submission_id)
        if data:
            osmid = get_osmid(data)
            if osmid:
                sp.data = data
                sp.save()

            return osmid


@app.task
def add_unique_record(pk, location_pk):
    try:
        sp = SprayDay.objects.get(pk=pk)
        location = Location.objects.get(pk=location_pk)
    except (SprayDay.DoesNotExist, Location.DoesNotExist):
        pass
    else:
        from mspray.apps.main.utils import add_unique_data
        osmid = get_osmid(sp.data) or get_updated_osm_from_ona(sp)
        if osmid:
            add_unique_data(sp, HAS_UNIQUE_FIELD, location)


@app.task
def link_spraypoint_with_osm(pk):
    try:
        sp = SprayDay.objects.get(pk=pk)
    except SprayDay.DoesNotExist:
        pass
    else:
        location, geom, is_node = get_location_from_osm(sp.data)
        if location is None:
            location, geom = get_new_structure_location(sp.data, geom, is_node)
            if location is None:
                location = get_location_from_data(sp.data)
            else:
                is_node = True
        set_spraypoint_location(sp, location, geom, is_node)

        return sp.pk


def _create_household(way, location):
    try:
        Household.objects.create(
            hh_id=way.get('osm_id'),
            geom=way.get('geom').centroid,
            bgeom=way.get('geom'),
            data=way.get('tags'),
            location=location
        )
    except Household.DoesNotExist:
        pass
    except IntegrityError:
        pass


@app.task
def process_osm_file(path):
    with open(path) as f:
        name = os.path.basename(path).replace('.osm', '')
        content = f.read()
        nodes = parse_osm(content.strip())
        ways = [
            way for way in nodes
            if not way.get('osm_id').startswith('-')
            and way.get('osm_type') == 'way'
        ]
        if ways:
            for way in ways:
                location = Location.objects.filter(
                    geom__contains=ways[0].get('geom'),
                    level='ta'
                ).first() or Location.objects.filter(
                        name=name, level='ta'
                    ).first()

                if location:
                    _create_household(way, location)
    gc.collect()


@app.task
def refresh_data_with_no_osm():
    data = SprayDay.objects.exclude(data__has_key='osmstructure:way:id')\
        .exclude(data__has_key='osmstructure:node:id')\
        .filter(data__has_key='osmstructure')
    found = data.count()
    for rec in data:
        osmid = get_updated_osm_from_ona(rec)
        if osmid:
            link_spraypoint_with_osm.delay(rec.pk)

    return found
