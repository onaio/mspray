import gc
import json

from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.utils import LayerMapping
from django.core.cache import cache
from django.db import connection
from django.db.models import Q, Count
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404

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
from mspray.apps.main.models.spraypoint import SprayPoint
from mspray.apps.main.models.spray_operator import DirectlyObservedSprayingForm
from mspray.apps.main.models.spray_operator import SprayOperatorDailySummary
from mspray.apps.main.models.spray_operator import SprayOperator
from mspray.apps.main.models.households_buffer import HouseholdsBuffer
from mspray.apps.main.models.spraypoint import SprayPointView
from mspray.apps.main.models.team_leader import TeamLeader
from mspray.apps.main.models.team_leader_assistant import TeamLeaderAssistant
from mspray.apps.main.tasks import link_spraypoint_with_osm
from mspray.libs.utils.geom_buffer import with_metric_buffer
from mspray.apps.main.tasks import run_tasks_after_spray_data


BUFFER_SIZE = getattr(settings, 'MSPRAY_NEW_BUFFER_WIDTH', 4)  # default to 4m
HAS_SPRAYABLE_QUESTION = settings.HAS_SPRAYABLE_QUESTION
SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE
TA_LEVEL = settings.MSPRAY_TA_LEVEL
WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
WAS_SPRAYED_VALUE = getattr(settings, 'MSPRAY_WAS_SPRAYED_VALUE', 'yes')
HAS_UNIQUE_FIELD = getattr(settings, 'MSPRAY_UNIQUE_FIELD', None)
SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE
TEAM_LEADER_CODE = settings.MSPRAY_TEAM_LEADER_CODE
IRS_NUMBER = settings.MSPRAY_IRS_NUM_FIELD
REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
REASON_REFUSED = settings.MSPRAY_UNSPRAYED_REASON_REFUSED
REASONS = settings.MSPRAY_UNSPRAYED_REASON_OTHER.copy()
REASONS.pop(REASON_REFUSED)
REASON_OTHER = REASONS.keys()


def get_formid(spray_operator, spray_date):
    return '%s.%s' % (spray_date.strftime('%d.%m'), spray_operator.code)


def geojson_from_gps_string(geolocation, geom=False):
    if not isinstance(geolocation, str):
        raise ValidationError('Expecting a a string for gps')

    geolocation = [float(p) for p in geolocation.split()[:2]]
    geolocation.reverse()
    if geom:
        return Point(geolocation[0], geolocation[1])

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
        where = "WHERE "\
            "ST_CoveredBy(geom, ST_GeomFromText('%s', 4326)) is true" % wkt

    cursor.execute(
        "UPDATE main_household SET bgeom = ST_GeomFromText(ST_AsText("
        "ST_Buffer(geography(geom), %s)), 4326) %s;" % (distance, where))


def create_households_buffer(distance=15, recreate=False, target=None):
    ta = None
    ta_qs = Location.objects.filter(level=TA_LEVEL)
    wkt = None

    if target:
        ta_qs = ta_qs.filter(code=target)
        wkt = ta.geom.wkt

    set_household_buffer(distance, wkt)

    if recreate:
        buffer_qs = HouseholdsBuffer.objects.all()

        if ta is not None:
            buffer_qs = buffer_qs.filter(geom__within=ta.geom)

        buffer_qs.delete()

    for ta in queryset_iterator(ta_qs, 10):
        hh_buffers = Household.objects.filter(location=ta)\
            .values_list('bgeom', flat=True)
        if len(hh_buffers) == 0:
            continue
        bf = MultiPolygon([hhb for hhb in hh_buffers])

        for b in bf.cascaded_union.simplify(settings.BUFFER_TOLERANCE):
            if not isinstance(b, Polygon):
                continue
            obj, created = \
                HouseholdsBuffer.objects.get_or_create(geom=b, location=ta)
            obj.num_households = \
                Household.objects.filter(geom__coveredby=b).count()
            obj.save()


def add_spray_data(data):
    """"
    Add spray data submission from aggregate submission to the dashboard
    """
    data = data.dict()
    submission_id = data.get(DATA_ID_FIELD)
    spray_date = data.get(DATE_FIELD)
    spray_date = datetime.strptime(spray_date, '%Y-%m-%d')
    gps_field = data.get(STRUCTURE_GPS_FIELD,
                         data.get(NON_STRUCTURE_GPS_FIELD))
    geom = geojson_from_gps_string(gps_field) \
        if gps_field is not None else None
    location_code = data.get(settings.MSPRAY_LOCATION_FIELD)
    location = None
    if location_code and not settings.MSPRAY_SPATIAL_QUERIES:
        location = Location.objects.get(code=location_code)
    elif geom is not None:
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

    if settings.OSM_SUBMISSIONS and geom is not None:
        sprayday.geom = geom
        sprayday.bgeom = with_metric_buffer(
            sprayday.geom, BUFFER_SIZE
        )

    so = get_spray_operator(data.get(SPRAY_OPERATOR_CODE))
    if so:
        sprayday.spray_operator = so
        sprayday.data['sprayformid'] = get_formid(so, spray_date)

    set_team_leader_assistant(sprayday, save=False)

    team_leader = get_team_leader(data.get(TEAM_LEADER_CODE))
    if team_leader:
        sprayday.team_leader = team_leader

    sprayday.save()

    if settings.OSM_SUBMISSIONS:
        link_spraypoint_with_osm.delay(sprayday.pk)

    unique_field = HAS_UNIQUE_FIELD
    if unique_field and location:
        add_unique_data(sprayday, unique_field, location)

    # run tasks after creating SprayDay obj
    if sprayday.has_osm_data():
        run_tasks_after_spray_data(sprayday)

    return sprayday


def set_team_leader_assistant(sprayday, save=True):
    team_leader_assistant = get_team_leader_assistant(
        sprayday.data.get(TEAM_LEADER_CODE)
    )
    if team_leader_assistant:
        sprayday.team_leader_assistant = team_leader_assistant
        if save:
            sprayday.save()


def get_dos_data(column, where_params=None):
    cursor = connection.cursor()
    where_clause = ''

    if where_params:
        sub_column = where_params.get('column')
        value = where_params.get('value')
        where_clause = """
where
    main_directlyobservedsprayingform.{sub_column} = '{value}'
""".format(**{'sub_column': sub_column, 'value': value})

    sql_statement = """
select
    {column},
    sum(case when correct_removal = 'yes' then 1 else 0 end) correct_removal_yes,
    sum(case when correct_mix = 'yes' then 1 else 0 end) correct_mix_yes,
    sum(case when rinse = 'yes' then 1 else 0 end) rinse_yes,
    sum(case when "PPE" = 'yes' then 1 else 0 end) ppe_yes,
    sum(case when "CFV" = 'yes' then 1 else 0 end) cfv_yes,
    sum(case when correct_covering = 'yes' then 1 else 0 end) correct_covering_yes,
    sum(case when leak_free = 'yes' then 1 else 0 end) leak_free_no,
    sum(case when correct_distance = 'yes' then 1 else 0 end) correct_distance_yes,
    sum(case when correct_speed = 'yes' then 1 else 0 end) correct_speed_yes,
    sum(case when correct_overlap = 'yes' then 1 else 0 end) correct_overlap_yes
from
    main_directlyobservedsprayingform
{where_clause}
group by
    {column};
""".format(**{'column': column, 'where_clause': where_clause})  # noqa

    cursor.execute(sql_statement)
    queryset = cursor.cursor.fetchall()

    return {
        a[0]: a[1:]
        for a in queryset
    }


def update_average_dos_score_all_levels(code, score):
    so = SprayOperator.objects.filter(code=code).first()
    if so:
        # update spray operator's average_spray_quality_score value
        so.average_spray_quality_score = round(score, 2)
        so.save()

        tl = so.team_leader
        spray_operators = tl.sprayoperator_set.values(
            'average_spray_quality_score'
        )

        # re-calculate and update average of team leader assistant
        numerator = sum([
            a.get('average_spray_quality_score') for a in spray_operators
        ])
        denominator = spray_operators.count() or 1
        average_spray_quality_score = numerator / denominator

        tl.average_spray_quality_score = round(average_spray_quality_score, 2)
        tl.save()

        # re-calculate and update average of district
        district = tl.location
        tl = district.teamleader_set.values(
            'average_spray_quality_score'
        )
        numerator = sum([
            a.get('average_spray_quality_score') for a in tl
        ])
        denominator = tl.count() or 1
        average_spray_quality_score = numerator / denominator

        district.average_spray_quality_score = round(
            average_spray_quality_score, 2
        )
        district.save()


def get_calculate_avg_dos_score(spray_operator_code):
    directly_observed_spraying_data = get_dos_data(
        'spray_date',
        {'column': 'sprayop_code_name', 'value': spray_operator_code}
    )

    total_positive_resp = 0
    for spray_date, records in directly_observed_spraying_data.items():
        if records:
            total_positive_resp += sum(records)

    return round(
        total_positive_resp / (len(directly_observed_spraying_data) or 1), 2
    )


def update_directly_observed(data, submission_id, spray_operator_code):
    """
    Updates an existing directly observed form.
    """
    dos = DirectlyObservedSprayingForm.objects.get(submission_id=submission_id)
    dos.correct_removal = data.get('correct_removal')
    dos.correct_mix = data.get('correct_mix')
    dos.rinse = data.get('rinse')
    dos.PPE = data.get('PPE')
    dos.CFV = data.get('CFV')
    dos.correct_covering = data.get('correct_covering')
    dos.leak_free = data.get('leak_free')
    dos.correct_distance = data.get('correct_distance')
    dos.correct_speed = data.get('correct_speed')
    dos.correct_overlap = data.get('correct_overlap')
    dos.district = data.get('district')
    dos.health_facility = data.get('health_facility')
    dos.supervisor_name = data.get('supervisor_name')
    dos.sprayop_code_name = spray_operator_code
    dos.tl_code_name = data.get('tl_code_name')
    dos.data = data
    dos.spray_date = data.get('today')
    dos.save()


def add_directly_observed_spraying_data(data):
    spray_operator_code = data.get('sprayop_code_name')
    submission_id = data.get('_id')
    try:
        update_directly_observed(data, submission_id, spray_operator_code)
    except DirectlyObservedSprayingForm.DoesNotExist:
        pass
    else:
        try:
            DirectlyObservedSprayingForm.objects.create(
                submission_id=submission_id,
                correct_removal=data.get('correct_removal'),
                correct_mix=data.get('correct_mix'),
                rinse=data.get('rinse'),
                PPE=data.get('PPE'),
                CFV=data.get('CFV'),
                correct_covering=data.get('correct_covering'),
                leak_free=data.get('leak_free'),
                correct_distance=data.get('correct_distance'),
                correct_speed=data.get('correct_speed'),
                correct_overlap=data.get('correct_overlap'),
                district=data.get('district'),
                health_facility=data.get('health_facility'),
                supervisor_name=data.get('supervisor_name'),
                sprayop_code_name=spray_operator_code,
                tl_code_name=data.get('tl_code_name'),
                data=data,
                spray_date=data.get('today'),
            )
        except IntegrityError:
            pass
    avg_dos_score = get_calculate_avg_dos_score(spray_operator_code)
    update_average_dos_score_all_levels(spray_operator_code, avg_dos_score)


def get_hh_submission(spray_form_id):
    hh_submission = SprayPointView.objects.filter(
        sprayformid=spray_form_id
    ).values(
        'sprayformid'
    ).annotate(
        sprayformid_count=Count('sprayformid'),
        sprayed_count=Count('was_sprayed')
    )

    return hh_submission and hh_submission[0] or {}


def get_sop_submission(spray_form_id):
    sop_submission = SprayOperatorDailySummary.objects.filter(
        spray_form_id=spray_form_id
    ).values(
        'spray_form_id'
    ).annotate(
        found_count=Count('found'),
        sprayed_count=Count('sprayed')
    )

    return sop_submission and sop_submission[0] or {}


def calculate_data_quality_check(spray_form_id, spray_operator_code):
    # from HH Submission form total submissions
    hh_submission_agg = get_hh_submission(spray_form_id)

    # from SOP Summary form
    sop_submission_aggregate = get_sop_submission(spray_form_id)

    sop_found_count = None
    if hh_submission_agg:
        hh_sprayformid_count = hh_submission_agg.get('sprayformid_count')
        hh_sprayed_count = hh_submission_agg.get('sprayed_count')

        sop_submission = sop_submission_aggregate.get(spray_form_id)
        if sop_submission:
            sop_found_count = sop_submission.get('found_count')
            sop_sprayed_count = sop_submission.get('sprayed_count')

    data_quality_check = False
    if sop_found_count is not None:
        # check HH Submission Form total submissions count is equal to
        # SOP Summary Form 'found' count and HH Submission Form
        # 'was_sprayed' count is equal to SOP Summary Form 'sprayed'
        # count and both checks should be based on 'sprayformid'
        data_quality_check = sop_found_count == hh_sprayformid_count\
            and sop_sprayed_count == hh_sprayed_count

    so = SprayOperator.objects.filter(code=spray_operator_code).first()
    if so:
        # update spray operator
        so.data_quality_check = data_quality_check
        so.save()

        team_leader_assistant = so.team_leader_assistant
        if data_quality_check:
            # if data_quality_check is True, check if all data quality
            # values for the rest of the spray operators is true before
            # saving
            data_quality_check = all(
                [
                    a.get('data_quality_check')
                    for a in team_leader_assistant.sprayoperator_set.values(
                        'data_quality_check'
                    )
                ]
            )

        # update team leader
        team_leader_assistant.data_quality_check = data_quality_check
        team_leader_assistant.save()

        # update district
        district = team_leader_assistant.location
        if data_quality_check:
            data_quality_check = all(
                [
                    a.get('data_quality_check')
                    for a in district.teamleaderassistant_set.values(
                        'data_quality_check'
                    )
                ]
            )

        district.data_quality_check = data_quality_check
        district.save()


def add_spray_operator_daily(data):
    submission_id = data.get(DATA_ID_FIELD)
    spray_date = data.get(DATE_FIELD)
    sprayed = data.get('sprayed', 0)
    found = data.get('found', 0)
    spray_operator_code = data.get('sprayop_code')
    so = get_spray_operator(spray_operator_code)
    spray_date = datetime.strptime(spray_date, '%Y-%m-%d')
    spray_form_id = data.get('sprayformid', get_formid(so, spray_date))
    data['sprayformid'] = spray_form_id
    try:
        SprayOperatorDailySummary.objects.create(
            spray_form_id=spray_form_id,
            sprayed=sprayed,
            found=found,
            submission_id=submission_id,
            sprayoperator_code=spray_operator_code,
            data=data,
        )
    except IntegrityError:
        pass
    else:
        calculate_data_quality_check(
            spray_form_id, spray_operator_code
        )


def get_team_leader(code):
    try:
        return TeamLeader.objects.get(code=code)
    except TeamLeader.DoesNotExist:
        pass

    return None


def get_team_leader_assistant(code):
    try:
        return TeamLeaderAssistant.objects.get(code=code)
    except TeamLeaderAssistant.DoesNotExist:
        pass
    return None


def get_spray_operator(code):
    try:
        return SprayOperator.objects.get(code=code)
    except SprayOperator.DoesNotExist:
        pass

    return None


def add_unique_data(sprayday, unique_field, location):
    sp = None
    wayid = unique_field + ':way:id'
    nodeid = unique_field + ':node:id'
    data_id = sprayday.data.get(wayid) or \
        sprayday.data.get(nodeid) or \
        sprayday.data.get('newstructure/gps')
    if data_id and location:
        if isinstance(data_id, str) and len(data_id) > 50:
            data_id = data_id[:50]
        try:
            sp, created = SprayPoint.objects.get_or_create(
                sprayday=sprayday,
                data_id=data_id,
                location=location
            )
        except IntegrityError:
            sp = SprayPoint.objects.select_related().get(
                data_id=data_id,
                location=location,
            )
            was_sprayed = sp.sprayday.data.get(WAS_SPRAYED_FIELD)

            if was_sprayed != WAS_SPRAYED_VALUE:
                sp.sprayday = sprayday
                sp.save()

    return sp


def delete_cached_target_area_keys(sprayday):
    locations = []

    if sprayday.geom is not None:
        locations = Location.objects.exclude(geom=None)
    elif sprayday.location is not None:
        locations = Location.objects.filter(
            Q(location=sprayday.location) |
            Q(location=sprayday.location.parent)
        )

    for location in locations:
        keys = "%(key)s_not_visited %(key)s_visited_other "\
            "%(key)s_visited_refused %(key)s_visited_sprayed "\
            "%(key)s_visited_total" % {'key': location.pk}
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


def avg_time(pks, field):
    # pks = list(qs.values_list('pk', flat=True))
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
    level = location['level'] if isinstance(location, dict) else location.level
    pk = location['pk'] if isinstance(location, dict) else location.pk

    if level == TA_LEVEL:
        locations = [pk]
    else:
        qs = Location.objects.filter(parent__pk=pk) \
            if isinstance(location, dict) else location.location_set.all()

        locations = Location.objects.filter(level=TA_LEVEL)\
            .filter(Q(parent__pk=pk) | Q(parent__in=qs))\
            .values_list('pk', flat=True)

    return locations


def get_sprayable_or_nonsprayable_queryset(queryset, yes_or_no):
    if HAS_SPRAYABLE_QUESTION:
        is_sprayable = yes_or_no == 'yes'

        return queryset.filter(sprayable=is_sprayable)

    return queryset


def sprayable_queryset(queryset):
    return get_sprayable_or_nonsprayable_queryset(queryset, 'yes')


def not_sprayable_queryset(queryset):
    return get_sprayable_or_nonsprayable_queryset(queryset, 'no')


def sprayed_queryset(queryset):
    return queryset.filter(was_sprayed=True)


def refused_queryset(queryset):
    return queryset.extra(
        where=['data->>%s = %s'],
        params=[REASON_FIELD, REASON_REFUSED]
    )


def other_queryset(queryset):
    return queryset.extra(
        where=[
            "data->>%s IN ({})".format(
                ",".join(["'{}'".format(i) for i in REASON_OTHER])
            )
        ],
        params=[REASON_FIELD]
    )


def unique_spray_points(queryset):
    if HAS_UNIQUE_FIELD:
        queryset = queryset.filter(
            pk__in=SprayPoint.objects.values('sprayday')
        )

    return queryset


def parse_spray_date(request):
    spray_date = request.GET.get('spray_date')
    if spray_date:
        try:
            return parse(spray_date).date()
        except ValueError:
            pass
    return None


def get_location_dict(code):
    data = {}
    if code:
        district = get_object_or_404(Location, pk=code)
        data['district'] = district
        data['district_code'] = district.pk
        data['district_name'] = district.name
        if district.level == settings.MSPRAY_TA_LEVEL:
            data['sub_locations'] = Location.objects\
                .filter(parent=district.parent)\
                .exclude(parent=None)\
                .values('id', 'level', 'name', 'parent')\
                .order_by('name')
            data['locations'] = Location.objects\
                .filter(parent=district.parent.parent)\
                .exclude(parent=None)\
                .values('id', 'level', 'name', 'parent')\
                .order_by('name')
        else:
            data['sub_locations'] = district.location_set.all()\
                .values('id', 'level', 'name', 'parent')\
                .order_by('name')
            data['locations'] = Location.objects\
                .filter(parent=district.parent)\
                .exclude(parent=None)\
                .values('id', 'level', 'name', 'parent')\
                .order_by('name')
        data['top_level'] = Location.objects.filter(parent=None)\
            .values('id', 'level', 'name', 'parent')\
            .order_by('name')
    if 'top_level' not in data:
        data['locations'] = Location.objects.filter(parent=None)\
            .values('id', 'level', 'name', 'parent')\
            .order_by('name')
    data['ta_level'] = settings.MSPRAY_TA_LEVEL
    data['higher_level_map'] = settings.HIGHER_LEVEL_MAP

    return data
