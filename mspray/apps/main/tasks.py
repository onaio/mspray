from __future__ import absolute_import

import gc
import os

from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models import Sum
from django.db.utils import IntegrityError
from django.utils import timezone

from mspray.apps.main.models import Household
from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import SprayOperatorDailySummary
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
FORM_ID = getattr(settings, 'ONA_FORM_PK', None)
LOCATION_VISITED_PERCENTAGE = getattr(
    settings, 'LOCATION_VISITED_PERCENTAGE', 20)
LOCATION_SPRAYED_PERCENTAGE = getattr(
    settings, 'LOCATION_SPRAYED_PERCENTAGE', 90)
UPDATE_VISITED_MINUTES = getattr(settings, 'UPDATE_VISITED_MINUTES', 5)


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
    if FORM_ID:
        data = fetch_form_data(FORM_ID, dataid=sp.submission_id)
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
            if way.get('osm_type') == 'way'
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


def set_sprayed_visited(location):
    from mspray.apps.main.serializers.target_area import get_spray_area_count
    if location.level == 'ta':
        sprayed = 0
        visited = 0
        visited_sprayed, found = get_spray_area_count(location)
        if visited_sprayed:
            ratio = round((visited_sprayed * 100) / found)
            if ratio >= LOCATION_VISITED_PERCENTAGE:
                visited = 1
            if ratio >= LOCATION_SPRAYED_PERCENTAGE:
                sprayed = 1

        location.visited = visited
        location.sprayed = sprayed
        location.save()
    else:
        queryset = location.location_set.values('id').aggregate(
            visited_sum=Sum('visited', distinct=True),
            sprayed_sum=Sum('sprayed', distinct=True)
        )
        location.visited = queryset.get('visited_sum') or 0
        location.sprayed = queryset.get('sprayed_sum') or 0
        location.save()


@app.task
def update_sprayed_visited(time_within=UPDATE_VISITED_MINUTES):
    """
    Sets 'sprayed' and 'visited' values for locations on submissions within
    UPDATE_VISITED_MINUTES which defaults to every 5 minutes.
    """
    def _set_sprayed_visited(key):
        for loc_id in submissions.values_list(key, flat=True).distinct():
            location = Location.objects.get(pk=loc_id)
            set_sprayed_visited(location)

    time_since = timezone.now() - timedelta(minutes=time_within + 1)
    submissions = SprayDay.objects.filter(created_on__gte=time_since)\
        .exclude(location__isnull=True)

    # spray areas
    _set_sprayed_visited('location')

    # RHC
    _set_sprayed_visited('location__parent')

    # District
    _set_sprayed_visited('location__parent__parent')


@app.task
def set_district_sprayed_visited():
    from mspray.apps.main.serializers.target_area import get_spray_area_count
    from mspray.apps.main.serializers.target_area import count_key_if_percent

    qs = Location.objects.filter(level='ta')
    for location in qs.iterator():
        set_sprayed_visited(location)

    gc.collect()
    qs = Location.objects.filter(level='RHC').values('id').annotate(
        visited_sum=Sum('location__visited', distinct=True),
        sprayed_sum=Sum('location__sprayed', distinct=True)
    )
    d = {}
    e = {}
    for l in qs:
        location = Location.objects.get(pk=l.get('id'))
        location.visited = l.get('visited_sum') or 0
        location.sprayed = l.get('sprayed_sum') or 0
        location.save()
        k = count_key_if_percent(location, 'sprayed',
                                 LOCATION_VISITED_PERCENTAGE)
        if k != location.visited:
            print(location, location.visited, k)
        k = count_key_if_percent(location, 'sprayed',
                                 LOCATION_SPRAYED_PERCENTAGE)
        if k != location.sprayed:
            print(location, location.sprayed, k)
        if location.parent_id not in d:
            d[location.parent_id] = 0
        d[location.parent_id] += location.visited
        if location.parent_id not in e:
            e[location.parent_id] = 0
        e[location.parent_id] += location.visited

    gc.collect()
    qs = Location.objects.filter(level='district').values('id').annotate(
        visited_sum=Sum('location__visited', distinct=True),
        sprayed_sum=Sum('location__sprayed', distinct=True)
    )
    for l in qs:
        location = Location.objects.get(pk=l.get('id'))
        location.visited = l.get('visited_sum') or 0
        location.sprayed = l.get('sprayed_sum') or 0
        location.save()
        k = count_key_if_percent(location, 'sprayed',
                                 LOCATION_VISITED_PERCENTAGE)
        if k != location.visited:
            print(location.pk, location, location.visited, k,
                  location.visited - k, d.get(location.pk))
        k = count_key_if_percent(location, 'sprayed',
                                 LOCATION_SPRAYED_PERCENTAGE)
        if k != location.sprayed:
            print(location.pk, location, location.sprayed, k,
                  location.sprayedt - k, e.get(location.pk))
    gc.collect()


@app.task
def remove_deleted_records():
    count = 0
    if FORM_ID:
        data = fetch_form_data(FORM_ID, dataids_only=True)
        pks = [i['_id'] for i in data]
        deleted_submissions = SprayDay.objects.exclude(submission_id__in=pks)
        count = deleted_submissions.count()
        deleted_submissions.delete()

    return count


@app.task
def update_edited_records():
    """
    Update edited records.
    """
    count = 0
    if FORM_ID:
        data = fetch_form_data(FORM_ID, dataids_only=True, edited_only=True)
        pks = [i['_id'] for i in data]
        edited_submissions = SprayDay.objects.filter(submission_id__in=pks)
        for rec in edited_submissions:
            data = fetch_form_data(FORM_ID, dataid=rec.submission_id)
            if data:
                from mspray.apps.main.utils import add_spray_data
                add_spray_data(data)
                count += 1

    return count


@app.task
def remove_deleted_daily_summary_records():
    """
    Deletes deleted Daily Summary records.
    """
    count = 0
    summary = SprayOperatorDailySummary.objects.last()
    formid = summary and summary.data.get('_xform_id')
    if formid:
        data = fetch_form_data(formid, dataids_only=True)
        pks = [i['_id'] for i in data]
        records = SprayOperatorDailySummary.objects.exclude(
            submission_id__in=pks)
        count = records.count()
        records.delete()

    return count
