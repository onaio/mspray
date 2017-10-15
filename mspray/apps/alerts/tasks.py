import operator
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from mspray.apps.warehouse.druid import get_druid_data, process_druid_data
from mspray.apps.warehouse.druid import process_location_data
from mspray.apps.alerts.rapidpro import start_flow
from mspray.apps.alerts.serializers import UserDistanceSerializer
from mspray.apps.alerts.serializers import RapidProBaseSerializer
from mspray.apps.alerts.serializers import FoundCoverageSerializer
from mspray.celery import app
from mspray.apps.main.models import Location, SprayDay, TeamLeader


@app.task
def weekly_dashboard_update():
    """
    Goes through eahc district and if there was data collected in the last
    week, sends an email update of the summary of activites during that week
    """
    dimensions = ['target_area_id', 'target_area_name',
                  'target_area_structures', 'rhc_id', 'rhc_name',
                  'district_id', 'district_name']
    today = timezone.now()
    # 8 days because we want the day just before
    one_week_ago = today - timedelta(days=8)
    districts = Location.objects.filter(level='district')
    for district in districts:
        filters = [['district_id', operator.eq, district.id],
                   ['spray_date', operator.gt,
                    one_week_ago.strftime('%Y-%m-%d')]]
        druid_result = get_druid_data(dimensions, filters)
        data, _ = process_druid_data(druid_result)


@app.task
def daily_spray_success_by_spray_area(district_id, spray_date):
    """
    Gets spray success rates for all the spray areas in a district, for a
    specific date.  If data is found, prepares a payload and sends it to
    RapidPro - which decides what to do with the payload.

    spray_date format == 2016-10-15
    """
    dimensions = ['target_area_id', 'target_area_name',
                  'target_area_structures', 'rhc_id', 'rhc_name',
                  'district_id', 'district_name']
    filters = [['district_id', operator.eq, district_id],
               ['spray_date', operator.eq, spray_date]]
    druid_result = get_druid_data(dimensions, filters)
    data, _ = process_druid_data(druid_result)
    if data:
        flow_uuid = settings.RAPIDPRO_DAILY_SPRAY_SUCCESS_FLOW_ID
        for item in data:
            payload = RapidProBaseSerializer(item, date=spray_date)
            return start_flow(flow_uuid, payload)


@app.task
def daily_found_coverage_by_spray_area(district_id, spray_date):
    """
    Gets spray coverage data for spray areas in a district and compares this
    with the same data for other areas, as well as data from the same spray
    area for different dates.
    Then prepares a payload to send to RapidPro for further proccessing.

    spray_date format == 2016-10-15
    """
    try:
        this_district = Location.objects.get(id=district_id)
    except Location.DoesNotExist:
        pass
    else:
        flow_uuid = settings.RAPIDPRO_DAILY_FOUND_COVERAGE_FLOW_ID
        target_areas = this_district.get_descendants().filter(level='ta')
        for target_area in target_areas:
            dimensions = ['target_area_id', 'target_area_name',
                          'target_area_structures', 'rhc_id', 'rhc_name',
                          'district_id', 'district_name']

            filters = [['target_area_id', operator.eq, target_area.id],
                       ['spray_date', operator.eq, spray_date]]
            # get today's data for this spray area
            druid_result1 = get_druid_data(dimensions, filters)
            today_data, _ = process_druid_data(druid_result1)
            # get today's data for all other spray areas
            druid_result2 = get_druid_data(
                dimensions=dimensions,
                filter_list=[['target_area_id', operator.ne, target_area.id],
                             ['spray_date', operator.eq, spray_date]])
            other_data, _ = process_druid_data(druid_result2)
            # get all data for this area for other dates
            druid_result3 = get_druid_data(
                dimensions=dimensions,
                filter_list=[['target_area_id', operator.eq, target_area.id],
                             ['spray_date', operator.ne, spray_date]])
            all_data, _ = process_druid_data(druid_result3)
            # prepare payload
            payload_source_data = {}
            if all_data:
                payload_source_data = all_data[0]

            if today_data:
                payload_source_data['has_submissions_today'] = 1
            else:
                payload_source_data['has_submissions_today'] = 0

            if other_data:
                payload_source_data['today_is_working_day'] = 1
            else:
                payload_source_data['today_is_working_day'] = 0

            payload = FoundCoverageSerializer(payload_source_data,
                                              date=spray_date,
                                              target_area=target_area)

            return start_flow(flow_uuid, payload.data)


@app.task
def user_distance(spray_day_obj_id):
    """
    calculates the distance between a user and the structure and sends
    payload to RapidPro
    """

    try:
        spray_day_obj = SprayDay.objects.get(pk=spray_day_obj_id)
    except SprayDay.DoesNotExist:
        pass
    else:
        payload = UserDistanceSerializer(spray_day_obj).data
        flow_uuid = settings.RAPIDPRO_USER_DISTANCE_FLOW_ID
        return start_flow(flow_uuid, payload)


@app.task
def so_daily_form_completion(district_code, so_code, confrimdecisionform):
    """
    Gets district name and surveillance officer name and packages them into
    payload for RapidPro
    """

    try:
        district = Location.objects.get(code=district_code, level='district')
    except Location.DoesNotExist:
        pass
    else:
        try:
            team_leader = TeamLeader.objects.get(code=so_code)
        except TeamLeader.DoesNotExist:
            pass
        else:
            payload = dict(so_name=team_leader.name,
                           district_name=district.name,
                           confrimdecisionform=confrimdecisionform)
            flow_uuid = settings.RAPIDPRO_SO_DAILY_COMPLETION_FLOW_ID
            return start_flow(flow_uuid, payload)


@app.task
def no_revisit(target_area_code, no_revisit_reason):
    """
    Retrieve target area spray data using target_area_code
    then package for sending to RapidPro
    """
    try:
        target_area = Location.objects.get(code=target_area_code, level='ta')
    except Location.DoesNotExist:
        pass
    else:
        dimensions = ['target_area_id', 'target_area_name',
                      'target_area_structures', 'rhc_id', 'rhc_name',
                      'district_id', 'district_name']
        filters = [['target_area_id', operator.eq, target_area.id]]
        # get today's data for this spray area
        druid_result = get_druid_data(dimensions, filters)
        data, _ = process_druid_data(druid_result)
        if data:
            payload = FoundCoverageSerializer(data[0], target_area=target_area)
        else:
            payload = FoundCoverageSerializer({}, target_area=target_area)
        payload = payload.data
        payload['no_revisit_reason'] = no_revisit_reason
        flow_uuid = settings.RAPIDPRO_NO_REVISIT_FLOW_ID
        return start_flow(flow_uuid, payload)


@app.task
def health_facility_catchment_hook():
    """
    starts the health_facility_catchment task
    """
    yesterday = timezone.now() - timedelta(days=1)
    processed_rhcs = []
    records = SprayDay.objects.filter(created_on__gte=yesterday)
    for record in records:
        if record.location.parent not in processed_rhcs:
            processed_rhcs.append(record.location.parent)
            health_facility_catchment.delay(record.id)


@app.task
def health_facility_catchment(spray_day_obj_id, force=False):
    """
    Checks each submission for evidence that it represents data from a new
    RHC.  If this is the case, then we send a summary of the 'previous RHC'
    """

    try:
        spray_day_obj = SprayDay.objects.get(pk=spray_day_obj_id)
    except SprayDay.DoesNotExist:
        pass
    else:
        current_rhc = spray_day_obj.location.parent

        if current_rhc:
            should_continue = False

            if force:
                should_continue = True
            else:
                threshold = settings.HEALTH_FACILITY_CATCHMENT_THRESHOLD
                upper_threshold = threshold * 2
                # count number of records for this RHC
                current_rhc_records = SprayDay.objects.filter(
                    location__parent=current_rhc).count()
                if upper_threshold >= current_rhc_records >= threshold:
                    should_continue = True

            if should_continue:
                # get previous RHC by looking for RHC with records from a
                # previous date
                previous_record = SprayDay.objects.exclude(
                    location__parent__id=current_rhc.id).filter(
                    location__parent__parent__id=current_rhc.parent.id).filter(
                    spray_date__lt=spray_day_obj.spray_date).order_by(
                    '-spray_date').first()
                previous_rhc = None
                if previous_record:
                    previous_rhc = previous_record.location.parent
                if previous_rhc:
                    # get summary data and send to flow
                    dimensions = ['target_area_id', 'target_area_name',
                                  'target_area_structures', 'rhc_id',
                                  'rhc_name', 'district_id', 'district_name']
                    filters = [['rhc_id', operator.eq, previous_rhc.id]]
                    druid_result = get_druid_data(dimensions, filters)
                    data, _ = process_druid_data(druid_result)
                    payload = process_location_data(previous_rhc.__dict__,
                                                    data)
                    payload['rhc_id'] = previous_rhc.id
                    payload['rhc_name'] = previous_rhc.name
                    payload['sprayed_coverage'] = int(
                        payload['sprayed_coverage'])
                    payload['sprayed_percentage'] = int(
                        payload['sprayed_percentage'])
                    payload['visited_percentage'] = int(
                        payload['visited_percentage'])
                    if previous_rhc.parent:
                        payload['district_id'] = previous_rhc.parent.id
                        payload['district_name'] = previous_rhc.parent.name
                    flow_uuid = settings.RAPIDPRO_HF_CATCHMENT_FLOW_ID
                    return start_flow(flow_uuid, payload)
