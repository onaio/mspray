import gc
import json

from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.utils import LayerMapping
from django.core.cache import cache
from django.db import connection
from django.core.exceptions import ValidationError

from mspray.apps.main.models.location import Location
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.models.target_area import namibia_mapping
from mspray.apps.main.models.household import Household
from mspray.apps.main.models.household import household_mapping
from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.spray_day import sprayday_mapping
from mspray.apps.main.models.spray_day import DATA_ID_FIELD
from mspray.apps.main.models.spray_day import DATE_FIELD
from mspray.apps.main.models.spray_day import STRUCTURE_GPS_FIELD
from mspray.apps.main.models.spray_day import NON_STRUCTURE_GPS_FIELD
from mspray.apps.main.models.households_buffer import HouseholdsBuffer

SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE


def geojson_from_gps_string(geolocation):
    if not isinstance(geolocation, str):
        raise ValidationError('Expecting a a string for gps')

    geolocation = [float(p) for p in geolocation.split()[:2]]
    geolocation.reverse()

    return json.dumps(
        {'type': 'point', 'coordinates': geolocation})


def queryset_iterator(queryset, chunksize=100):
    '''''
    Iterate over a Django Queryset.

    This method loads a maximum of chunksize (default: 100) rows in
    its memory at the same time while django normally would load all
    rows in its memory. Using the iterator() method only causes it to
    not preload all the classes.
    '''
    start = 0
    end = chunksize
    while start < queryset.count():
        for row in queryset[start:end]:
            yield row
        start += chunksize
        end += chunksize
        gc.collect()


def load_layer_mapping(model, shp_file, mapping, verbose=False, unique=None):
    lm = LayerMapping(model, shp_file, mapping, transform=True, unique=unique)
    lm.save(strict=True, verbose=verbose)


def load_area_layer_mapping(shp_file, verbose=False):
    unique = 'targetid'
    load_layer_mapping(TargetArea, shp_file, namibia_mapping, verbose,
                       unique)


def load_household_layer_mapping(shp_file, verbose=False):
    unique = None  # 'orig_fid'
    load_layer_mapping(Household, shp_file, household_mapping, verbose, unique)


def load_sprayday_layer_mapping(shp_file, verbose=False):
    load_layer_mapping(SprayDay, shp_file, sprayday_mapping, verbose)


def set_household_buffer(distance=15, wkt=None):
    cursor = connection.cursor()
    where = ""
    if wkt is not None:
        where = "WHERE ST_CoveredBy(geom, ST_GeomFromText('%s', 4326)) is true" \
            % wkt

    cursor.execute(
        "UPDATE main_household SET bgeom = ST_GeomFromText(ST_AsText("
        "ST_Buffer(geography(geom), %s)), 4326) %s;" % (distance, where))


def create_households_buffer(distance=15, recreate=False, target=None):
    ta = None
    ta_qs = TargetArea.objects.filter()
    wkt = None

    if target:
        ta = TargetArea.objects.get(rank_house=target)
        ta_qs = ta_qs.filter(pk=ta.pk)
        wkt = ta.geom.wkt

    set_household_buffer(distance, wkt)

    if recreate:
        buffer_qs = HouseholdsBuffer.objects.all()

        if ta is not None:
            buffer_qs = buffer_qs.filter(geom__within=ta.geom)

        buffer_qs.delete()

    for ta in queryset_iterator(ta_qs, 10):
        hh_buffers = Household.objects.filter(geom__coveredby=ta.geom)\
            .values_list('bgeom', flat=True)
        if len(hh_buffers) == 0:
            continue
        bf = MultiPolygon([hhb for hhb in hh_buffers])

        for b in bf.cascaded_union.simplify(settings.BUFFER_TOLERANCE):
            if not isinstance(b, Polygon):
                continue
            obj, created = \
                HouseholdsBuffer.objects.get_or_create(geom=b, target_area=ta)
            obj.num_households = \
                Household.objects.filter(geom__coveredby=b).count()
            obj.save()


def add_spray_data(data):
    """"
    Add spray data submission from aggregate submission to the dashboard
    """
    submission_id = data.get(DATA_ID_FIELD)
    spray_date = data.get(DATE_FIELD)
    spray_date = datetime.strptime(spray_date, '%Y-%m-%d')
    gps_field = data.get(STRUCTURE_GPS_FIELD,
                         data.get(NON_STRUCTURE_GPS_FIELD))
    geom = geojson_from_gps_string(gps_field)
    location_code = data.get(settings.MSPRAY_LOCATION_FIELD)
    location = None
    if location_code and not settings.MSPRAY_SPATIAL_QUERIES:
        location = Location.objects.get(code=location_code)
    else:
        locations = Location.objects.filter(
            geom__contains=geom,
            level=settings.MSPRAY_TA_LEVEL
        )
        if locations:
            location = locations[0]

    sprayday, created = SprayDay.objects.get_or_create(
        submission_id=submission_id,
        spray_date=spray_date,
        geom=geom,
        location=location
    )
    sprayday.data = data

    sprayday.save()

    return sprayday


def delete_cached_target_area_keys(sprayday):
    for t in TargetArea.objects.filter(geom__contains=sprayday.geom):
        keys = "%(key)s_not_visited %(key)s_visited_other "\
            "%(key)s_visited_refused %(key)s_visited_sprayed "\
            "%(key)s_visited_total" % {'key': t.pk}
        cache.delete_many(keys.split())


def avg_time_per_group(results):
        partition = {}
        for op, day, hour, minute in results:
            if op not in partition:
                partition[op] = []
            partition[op].append((hour, minute))

        times = []
        for k, v in partition.items():
            times.append(avg_time_tuple(v))

        return avg_time_tuple(times) if len(times) else (None, None)


def avg_time(qs, field):
    pks = list(qs.values_list('pk', flat=True))
    if len(pks) == 0:
        return (None, None)

    START = 'start'
    END = 'end'
    if field not in [START, END]:
        raise ValueError(
            "field should be either 'start' or 'end': {} is invalid."
            .format(field)
        )
    ORDER = 'ASC' if field == END else 'DESC'

    SQL = (
        "SELECT spray_operator, today, "
        "EXTRACT(HOUR FROM to_timestamp(endtime,'YYYY-MM-DD HH24:MI:SS.MS')) "
        "as hour, EXTRACT(MINUTE FROM "
        "to_timestamp(endtime,'YYYY-MM-DD HH24:MI:SS.MS')) as minute FROM "
        "(SELECT (data->>%s) AS spray_operator, data->>'today' AS"
        " today, data->>%s AS endtime, ROW_NUMBER() OVER (PARTITION BY "
        "(data->>%s), data->>'today' ORDER BY data->>%s " + ORDER + ") "
        "FROM main_sprayday WHERE (data->%s) IS NOT NULL AND "
        "data->>'today' = SUBSTRING(data->>%s, 0, 11) AND id IN %s) as Q1"
        " WHERE row_number = 1;"
    )
    params = [SPRAY_OPERATOR_CODE, field, SPRAY_OPERATOR_CODE, field,
              SPRAY_OPERATOR_CODE, field, tuple(pks)]
    cursor = connection.cursor()
    cursor.execute(SQL, params)

    return avg_time_per_group(cursor.fetchall())


def avg_time_tuple(times):
    """Takes a list of tuples and calculates the average"""
    results = []
    for hour, minute in times:
        if hour is not None and minute is not None:
            results.append(timedelta(hours=hour, minutes=minute).seconds)
    if len(results):
        result = sum(results) / len(results)
        minutes, seconds = divmod(result, 60)
        hours, minutes = divmod(minutes, 60)

        return (round(hours), round(minutes))

    return None


def get_ta_in_location(location):
    locations = []

    if location.level == settings.MSPRAY_TA_LEVEL:
        locations = [location.pk]
    else:
        for loc in location.location_set.all():
            locations.extend(get_ta_in_location(loc))

    return locations
