from __future__ import absolute_import

import gc
import os
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.geos.polygon import Polygon
from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce
from django.db.utils import IntegrityError
from django.utils import timezone

from mspray.apps.alerts.tasks import no_gps, user_distance
from mspray.apps.main.models import (
    DirectlyObservedSprayingForm,
    Household,
    Location,
    Mobilisation,
    SensitizationVisit,
    SprayDay,
    SprayOperatorDailySummary,
    WeeklyReport,
)
from mspray.apps.main.models.mobilisation import create_mobilisation_visit
from mspray.apps.main.models.sensitization_visit import (
    create_sensitization_visit
)
from mspray.apps.main.models.spray_day import (
    NON_STRUCTURE_GPS_FIELD,
    STRUCTURE_GPS_FIELD,
    get_osmid,
)
from mspray.apps.warehouse.tasks import stream_to_druid
from mspray.celery import app
from mspray.libs.ona import fetch_form_data, fetch_osm_xml
from mspray.libs.osm import parse_osm, parse_osm_nodes, parse_osm_ways
from mspray.libs.utils.geom_buffer import with_metric_buffer

BUFFER_SIZE = getattr(settings, "MSPRAY_NEW_BUFFER_WIDTH", 4)  # default to 4m
HAS_UNIQUE_FIELD = getattr(settings, "MSPRAY_UNIQUE_FIELD", None)
STRUCTURE_GPS_FIELD = getattr(
    settings, "MSPRAY_STRUCTURE_GPS_FIELD", STRUCTURE_GPS_FIELD
)
FORM_ID = getattr(settings, "ONA_FORM_PK", None)
LOCATION_VISITED_PERCENTAGE = getattr(
    settings, "LOCATION_VISITED_PERCENTAGE", 20
)
LOCATION_SPRAYED_PERCENTAGE = getattr(
    settings, "LOCATION_SPRAYED_PERCENTAGE", 90
)
UPDATE_VISITED_MINUTES = getattr(settings, "UPDATE_VISITED_MINUTES", 5)
DIRECTLY_OBSERVED_FORM_ID = getattr(
    settings, "DIRECTLY_OBSERVED_FORM_ID", None
)
DAILY_SUMMARY_FORM_PK = getattr(settings, "SOP_DAILY_SUMMARY_FORM_PK", None)
FALLBACK_TO_ODK = settings.FALLBACK_TO_SUBMISSION_DATA_LOCATION

logger = logging.getLogger(__name__)


def get_new_structure_location(data, geom, is_node=False):
    from mspray.apps.main.utils import geojson_from_gps_string

    if is_node and geom is None:
        gps_field = data.get(
            STRUCTURE_GPS_FIELD, data.get(NON_STRUCTURE_GPS_FIELD)
        )
        geom = (
            geojson_from_gps_string(gps_field, True)
            if gps_field is not None
            else geom
        )
    location = None
    if geom is not None:
        locations = Location.objects.filter(
            geom__contains=geom, target=True, level=settings.MSPRAY_TA_LEVEL
        )
        if locations:
            location = locations[0]

    return location, geom


def get_location_from_data(data):
    district = data.get("district")
    target_area = data.get("spray_area")
    location = None
    try:
        location = Location.objects.get(
            name=target_area, target=True, parent__parent__code=district
        )
    except Location.DoesNotExist:
        pass
    except ValueError:
        pass

    return location


def get_location_from_osm(data):
    geom = None
    is_node = False
    location = None
    filename = data.get(HAS_UNIQUE_FIELD)
    osm_xml = fetch_osm_xml(data, filename)
    if osm_xml is not None:
        geoms = []
        geoms = parse_osm_ways(osm_xml) or parse_osm_nodes(osm_xml)

        if len(geoms):
            geom = geoms[0]["geom"]
            is_node = isinstance(geom, Point)
            locations = Location.objects.filter(
                geom__covers=geom, target=True, level=settings.MSPRAY_TA_LEVEL
            )
            if locations:
                location = locations.first()
        else:
            location = get_location_from_data(data)

    return location, geom, is_node


def set_spraypoint_location(sp, location, geom, is_node=False):
    if geom:
        sp.geom = geom.centroid if not is_node else geom
        sp.bgeom = (
            geom if not is_node else with_metric_buffer(sp.geom, BUFFER_SIZE)
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


def run_tasks_after_spray_data(sprayday):
    """
    Additional tasks to be run after receive new spray data submission.
    """
    if getattr(settings, "ENABLE_ALERTS", False):
        # no gps alert
        no_gps.delay(sprayday.id)
        # user distance alert
        user_distance.delay(sprayday.id)

    # stream to druid
    if getattr(settings, "STREAM_TO_DRUID", False):
        stream_to_druid.delay(sprayday.id)


@app.task
def add_unique_record(sprayday_pk, location_pk):
    """Add a spraypoint for the submission."""
    try:
        sprayday = SprayDay.objects.get(pk=sprayday_pk)
        location = Location.objects.get(pk=location_pk)
    except (SprayDay.DoesNotExist, Location.DoesNotExist):
        pass
    else:
        from mspray.apps.main.utils import add_unique_data

        osmid = (
            get_osmid(sprayday.data)
            or get_updated_osm_from_ona(sprayday)
            or sprayday.data.get("newstructure/gps")
        )
        if osmid:
            try:
                osmid = int(osmid)
            except ValueError:
                pass
            else:
                if osmid > 0:
                    # see if we have a matching household structure
                    try:
                        Household.objects.get(hh_id=osmid)
                    except Household.DoesNotExist:
                        try:
                            household = Household.objects.get(
                                bgeom=sprayday.bgeom
                            )
                        except Household.DoesNotExist:
                            pass
                        else:
                            osmid = household.hh_id
                            sprayday.osmid = osmid
                            sprayday.save()
                            sprayday.refresh_from_db()
            add_unique_data(sprayday, HAS_UNIQUE_FIELD, location, osmid)


@app.task
def link_spraypoint_with_osm(spray_day_id):
    """Use OSM to link a record to a location."""
    try:
        spray_day = SprayDay.objects.get(pk=spray_day_id)
    except SprayDay.DoesNotExist:
        pass
    else:
        location, geom, is_node = get_location_from_osm(spray_day.data)
        if location is None:
            location, geom = get_new_structure_location(
                spray_day.data, geom, is_node
            )
            if location is None and FALLBACK_TO_ODK:
                location = get_location_from_data(spray_day.data)
            else:
                is_node = isinstance(geom, Point)

        if not location and not FALLBACK_TO_ODK and not spray_day.location:
            spray_day.location = None

        set_spraypoint_location(spray_day, location, geom, is_node)

        return spray_day.pk


def _create_household(way, location):

    bgeom = None
    if isinstance(way.get("geom"), Polygon):
        bgeom = way.get("geom")

    try:
        Household.objects.create(
            hh_id=way.get("osm_id"),
            geom=way.get("geom").centroid,
            bgeom=bgeom,
            data=way.get("tags"),
            location=location,
        )
    except Household.DoesNotExist:
        pass
    except IntegrityError:
        pass


@app.task
def process_osm_file(path):
    with open(path) as f:
        name = os.path.basename(path).replace(".osm", "")
        content = f.read()
        nodes = parse_osm(content.strip())
        ways = [way for way in nodes if way.get("osm_type") == "way"]
        if ways:
            for way in ways:
                location = (
                    Location.objects.filter(
                        geom__contains=ways[0].get("geom"), level="ta"
                    ).first()
                    or Location.objects.filter(name=name, level="ta").first()
                )

                if location:
                    _create_household(way, location)
    gc.collect()


@app.task
def refresh_data_with_no_osm():
    def _process_no_osm(queryset):
        for rec in data:
            osmid = get_updated_osm_from_ona(rec)
            if osmid:
                link_spraypoint_with_osm.delay(rec.pk)

    data = (
        SprayDay.objects.exclude(data__has_key="osmstructure:way:id")
        .exclude(data__has_key="osmstructure:node:id")
        .filter(data__has_key="osmstructure")
    )
    found = data.count()
    _process_no_osm(data)

    data = SprayDay.objects.filter(geom__isnull=True)
    found = data.count() + found
    _process_no_osm(data)

    return found


def set_sprayed_visited_week(
    location, week_number, visited, sprayed, structures
):
    try:
        report = WeeklyReport.objects.get(
            location=location, week_number=week_number
        )
    except WeeklyReport.DoesNotExist:
        report = WeeklyReport(location=location, week_number=week_number)

    report.visited = visited
    report.sprayed = sprayed
    report.structures = structures
    report.save()


@app.task
def task_set_sprayed_visited(location_id, week_number=None):
    try:
        location = Location.objects.get(pk=location_id)
    except Location.DoesNotExist:
        pass
    else:
        set_sprayed_visited(location, week_number=week_number)


def set_sprayed_visited(location, week_number=None):
    """Set Sprayed Visited Function."""
    from mspray.apps.main.serializers.target_area import get_spray_area_stats

    if location.level == "ta":
        sprayed = 0
        visited = 0
        context = {"week_number": week_number}
        data, total_structures = get_spray_area_stats(location, context)
        found = location.visited_found
        visited_sprayed = data.get("sprayed")
        if total_structures > 0:
            if found:
                ratio = round((found * 100) / total_structures)
                if ratio >= LOCATION_VISITED_PERCENTAGE:
                    visited = 1

            if visited_sprayed:
                ratio = round((visited_sprayed * 100) / total_structures)
                if ratio >= LOCATION_SPRAYED_PERCENTAGE:
                    sprayed = 1

        if week_number:
            # print(week_number, location, week_number, visited, sprayed)
            set_sprayed_visited_week(
                location, week_number, visited, sprayed, total_structures
            )
        else:
            location.visited = visited
            location.sprayed = sprayed
            location.save()
    else:
        if week_number:
            kwargs = {"week_number": week_number}
            if location.level == "RHC":
                kwargs["location__parent"] = location
            else:
                kwargs["location__parent__parent"] = location
            queryset = WeeklyReport.objects.filter(**kwargs).aggregate(
                structures_sum=Coalesce(
                    Sum("structures", distinct=True), Value(0)
                ),
                visited_sum=Coalesce(Sum("visited", distinct=True), Value(0)),
                sprayed_sum=Coalesce(Sum("sprayed", distinct=True), Value(0)),
            )
            # print(week_number, location, week_number,
            #       queryset.get('visited_sum'), queryset.get('sprayed_sum'))
            set_sprayed_visited_week(
                location,
                week_number,
                queryset.get("visited_sum"),
                queryset.get("sprayed_sum"),
                queryset.get("structures_sum"),
            )
        else:
            queryset = location.location_set.values("id").aggregate(
                visited_sum=Coalesce(Sum("visited", distinct=True), Value(0)),
                sprayed_sum=Coalesce(Sum("sprayed", distinct=True), Value(0)),
            )
            location.visited = queryset.get("visited_sum") or 0
            location.sprayed = queryset.get("sprayed_sum") or 0
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
    submissions = SprayDay.objects.filter(created_on__gte=time_since).exclude(
        location__isnull=True
    )

    # spray areas
    _set_sprayed_visited("location")

    # RHC
    _set_sprayed_visited("location__parent")

    # District
    _set_sprayed_visited("location__parent__parent")


@app.task
def update_sprayed_visited_week(
    time_within=UPDATE_VISITED_MINUTES, week_number=None
):
    """
    Sets 'sprayed' and 'visited' values for locations on submissions within
    UPDATE_VISITED_MINUTES which defaults to every 5 minutes.
    """

    def _set_sprayed_visited(key):
        for loc_id in submissions.values_list(key, flat=True).distinct():
            location = Location.objects.get(pk=loc_id)
            set_sprayed_visited(location, week_number=week_number)

    # time_since = timezone.now() - timedelta(minutes=time_within + 1)
    # submissions = SprayDay.objects.filter(created_on__gte=time_since)\
    submissions = SprayDay.objects.filter().exclude(location__isnull=True)
    if not week_number:
        week_number = int(timezone.now().strftime("%W"))

    # spray areas
    _set_sprayed_visited("location")

    # RHC
    _set_sprayed_visited("location__parent")

    # District
    _set_sprayed_visited("location__parent__parent")


@app.task
def set_district_sprayed_visited():
    """
    Update sprayed and visited numbers on all objects.
    """
    queryset = Location.objects.filter(level="ta", target=True)
    for location in queryset.iterator():
        set_sprayed_visited(location)

    for location in Location.objects.filter(level="RHC"):
        set_sprayed_visited(location)

    for location in Location.objects.filter(level="district"):
        set_sprayed_visited(location)


@app.task
def remove_deleted_records():
    """Remove deleted records."""
    count = 0
    if FORM_ID:
        data = fetch_form_data(FORM_ID, dataids_only=True)
        if not data:
            return count

        pks = [i["_id"] for i in data]
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
        if not data:
            return count

        pks = [i["_id"] for i in data]
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
    formid = summary and summary.data.get("_xform_id")
    if formid:
        data = fetch_form_data(formid, dataids_only=True)
        if not data:
            return count

        pks = [i["_id"] for i in data]
        records = SprayOperatorDailySummary.objects.exclude(
            submission_id__in=pks
        )
        count = records.count()
        records.delete()

    return count


@app.task
def fetch_directly_observed():
    """
    Update edited records.
    """
    count = 0
    dos = DirectlyObservedSprayingForm.objects.last()
    formid = dos.data.get("_xform_id") if dos else DIRECTLY_OBSERVED_FORM_ID
    if formid:
        data = fetch_form_data(formid, dataids_only=True)
        if not data:
            return count

        pks = [i["_id"] for i in data]
        received = DirectlyObservedSprayingForm.objects.values_list(
            "submission_id", flat=True
        )
        new_ids = set(pks).difference(set((i for i in received)))

        for rec in new_ids:
            data = fetch_form_data(formid, dataid=rec)
            if data:
                from mspray.apps.main.utils import (
                    add_directly_observed_spraying_data
                )  # NOQA

                add_directly_observed_spraying_data(data)
                count += 1

    return count


@app.task
def fetch_updated_directly_observed():
    """
    Update edited records.
    """
    count = 0
    dos = DirectlyObservedSprayingForm.objects.last()
    formid = dos.data.get("_xform_id") if dos else DIRECTLY_OBSERVED_FORM_ID
    if formid:
        data = fetch_form_data(formid, dataids_only=True, edited_only=True)
        if not data:
            return count

        pks = [i["_id"] for i in data]
        for rec in pks:
            data = fetch_form_data(formid, dataid=rec)
            if data:
                from mspray.apps.main.utils import (
                    add_directly_observed_spraying_data
                )  # NOQA

                add_directly_observed_spraying_data(data)
                count += 1

    return count


@app.task
def remove_deleted_dos_records():
    """
    Remove directly observed records..
    """
    count = 0
    dos = DirectlyObservedSprayingForm.objects.last()
    formid = dos.data.get("_xform_id") if dos else DIRECTLY_OBSERVED_FORM_ID
    if formid:
        data = fetch_form_data(formid, dataids_only=True)
        if not data:
            return count

        pks = [i["_id"] for i in data]
        deleted_submissions = DirectlyObservedSprayingForm.objects.exclude(
            submission_id__in=pks
        )
        count = deleted_submissions.count()
        deleted_submissions.delete()

    return count


@app.task
def check_missing_data():
    """
    Sync missing spray data from Ona.
    """
    from mspray.apps.main.utils import sync_missing_sprays

    sync_missing_sprays(FORM_ID, print)


@app.task
def check_missing_sopdailysummary_data():
    """
    Sync missing SOP daily summary form data from Ona.
    """
    from mspray.apps.main.utils import sync_missing_sopdailysummary

    sync_missing_sopdailysummary(DAILY_SUMMARY_FORM_PK, print)


@app.task
def check_missing_unique_link():
    """
    Checks and forces a linking of submitted data that has not yet been
    identified as unique.
    """
    from mspray.apps.main.utils import queryset_iterator

    queryset = SprayDay.objects.filter(spraypoint__isnull=True).only(
        "pk", "location_id"
    )
    for record in queryset_iterator(queryset):
        add_unique_record(record.pk, record.location_id)
        gc.collect()


@app.task
def update_performance_reports(update_all=True):
    """
    Update performance records updated in the last UPDATE_VISITED_MINUTES
    minutes.
    """
    from mspray.apps.main.utils import performance_report

    time_within = UPDATE_VISITED_MINUTES
    time_since = timezone.now() - timedelta(minutes=time_within + 1)

    if update_all:
        submissions = SprayDay.objects.all()
    else:
        submissions = SprayDay.objects.filter(
            Q(created_on__gte=time_since) | Q(modified_on__gte=time_since)
        )

    sop_queryset = (
        SprayDay.objects.filter(
            Q(created_on__gte=time_since) | Q(modified_on__gte=time_since)
        )
        .filter(spray_operator__isnull=False)
        .only("spray_operator")
        .distinct("spray_operator")
    )

    for record in sop_queryset:
        performance_report(
            record.spray_operator,
            submissions.filter(spray_operator=record.spray_operator),
        )


@app.task
def sync_performance_reports():
    """
    Task to find missing performance reports and sync them back in
    """
    from mspray.apps.main.utils import find_missing_performance_report_records
    from mspray.apps.main.utils import performance_report
    from mspray.apps.main.utils import queryset_iterator

    missing_sprayformids = find_missing_performance_report_records()

    queryset = SprayDay.objects.filter(
        data__sprayformid__in=missing_sprayformids
    ).distinct("spray_operator")

    for record in queryset_iterator(queryset):
        performance_report(record.spray_operator)


def get_missing_ids(formid, target_class):
    """Return submission ids not yet synchronised."""
    data_ids = fetch_form_data(formid, dataids_only=True)
    if data_ids:
        data_ids = set(i["_id"] for i in data_ids)
        existing = set(
            i
            for i in target_class.objects.values_list(
                "submission_id", flat=True
            )
        )

        return data_ids - existing

    return []


@app.task
def fetch_sensitization_visits():
    """Fetch sensitization visit submissions."""
    formid = getattr(settings, "SENSITIZATION_VISIT_FORM_ID", None)
    if formid:
        data_ids = get_missing_ids(formid, SensitizationVisit)
        for data_id in data_ids:
            data = fetch_form_data(formid, dataid=data_id)
            if data:
                try:
                    create_sensitization_visit(data)
                except IntegrityError:
                    # Fail silently, likely we did not find the household
                    # matching the osm id.
                    pass


@app.task
def fetch_mobilisation():
    """Fetch mobilisation submissions."""
    formid = getattr(settings, "MOBILISATION_FORM_ID", None)
    if formid:
        data_ids = get_missing_ids(formid, Mobilisation)
        for data_id in data_ids:
            data = fetch_form_data(formid, dataid=data_id)
            if data:
                try:
                    create_mobilisation_visit(data)
                except IntegrityError:
                    logger.exception("{} Record not found.".format(formid))
                    continue
