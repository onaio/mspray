from __future__ import absolute_import

import gc
import os

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models import Sum
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
from mspray.libs.utils.geom_buffer import with_metric_buffer

BUFFER_SIZE = getattr(settings, 'MSPRAY_NEW_BUFFER_WIDTH', 4)  # default to 4m
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
    target_area = data.get('spray_area')
    location = None
    try:
        location = Location.objects.get(name=target_area,
                                        parent__parent__code=district)
    except Location.DoesNotExist:
        pass
        # if target_area == 'NM':
        #     code = 'NM{}'.format(district)
        #     location = Location.objects.get(code=code, parent__code=district)
    except ValueError:
        pass

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
        sp.bgeom = geom if not is_node else with_metric_buffer(
            sp.geom, BUFFER_SIZE
        )

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
        osmid = get_osmid(sp.data) or \
            get_updated_osm_from_ona(sp) or \
            sp.data.get('newstructure/gps')
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


@app.task
def set_district_sprayed_visited():
    from mspray.apps.main.serializers.target_area import get_spray_area_count
    from mspray.apps.main.serializers.target_area import count_key_if_percent

    qs = Location.objects.filter(level='ta')
    for location in qs.iterator():
        sprayed = 0
        visited = 0
        visited_sprayed, found = get_spray_area_count(location)
        if visited_sprayed:
            ratio = round((visited_sprayed * 100) / found)
            if ratio >= 20:
                visited = 1
            if ratio >= 85:
                sprayed = 1

        location.visited = visited
        location.sprayed = sprayed
        location.save()

    gc.collect()
    qs = Location.objects.filter(level='RHC').annotate(
        visited_sum=Sum('location__visited'),
        sprayed_sum=Sum('location__sprayed')
    )
    d = {}
    e = {}
    for location in qs:
        location.visited = location.visited_sum or 0
        location.sprayed = location.sprayed_sum or 0
        location.save()
        k = count_key_if_percent(location, 'sprayed', 20)
        if k != location.visited:
            print(location, location.visited, k)
        k = count_key_if_percent(location, 'sprayed', 85)
        if k != location.sprayed:
            print(location, location.spprayed, k)
        if location.parent_id not in d:
            d[location.parent_id] = 0
        d[location.parent_id] += location.visited
        if location.parent_id not in e:
            e[location.parent_id] = 0
        e[location.parent_id] += location.visited

    gc.collect()
    qs = Location.objects.filter(level='district').annotate(
        visited_sum=Sum('location__visited'),
        sprayed_sum=Sum('location__sprayed')
    )
    for location in qs:
        location.visited = location.visited_sum or 0
        location.sprayed = location.sprayed_sum or 0
        location.save()
        k = count_key_if_percent(location, 'sprayed', 20)
        if k != location.visited:
            print(location.pk, location, location.visited, k,
                  location.visited - k, d.get(location.pk))
        k = count_key_if_percent(location, 'sprayed', 85)
        if k != location.sprayed:
            print(location.pk, location, location.sprayed, k,
                  location.sprayedt - k, e.get(location.pk))
    gc.collect()
