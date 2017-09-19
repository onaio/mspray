import operator

from django.conf import settings

from mspray.apps.warehouse.druid import get_druid_data
from mspray.apps.alerts.rapidpro import start_flow
from mspray.apps.alerts.serializers import UserDistanceSerializer

from mspray.apps.main.models import Location, SprayDay


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
    data, _ = get_druid_data(dimensions, filters)
    if data:
        flow_uuid = settings.RAPIDPRO_DAILY_SPRAY_SUCCESS_FLOW_ID
        for item in data:
            payload = dict(
                target_area_id=item['target_area_id'],
                target_area_name=item['target_area_name'],
                rhc_id=item['rhc_id'],
                rhc_name=item['rhc_name'],
                district_id=item['district_id'],
                district_name=item['district_name'],
                num_found=item['num_found'],
                num_sprayed=item['num_sprayed_no_duplicates'],
                spray_coverage=int(item['spray_coverage']),
                found_coverage=int(item['found_coverage']),
                spray_effectiveness=int(item['spray_effectiveness']),
                total_structures=item['total_structures'],
                date=spray_date
            )
            start_flow(flow_uuid, payload)


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
            today_data, _ = get_druid_data(dimensions, filters)
            # get today's data for all other spray areas
            other_data, _ = get_druid_data(
                dimensions=dimensions,
                filter_list=[['target_area_id', operator.ne, target_area.id],
                             ['spray_date', operator.eq, spray_date]])
            # get all data for this area for other dates
            all_data, _ = get_druid_data(
                dimensions=dimensions,
                filter_list=[['target_area_id', operator.eq, target_area.id],
                             ['spray_date', operator.ne, spray_date]])
            # prepare payload
            payload = {}
            if today_data:
                payload['has_submissions_today'] = 1
            else:
                payload['has_submissions_today'] = 0

            if other_data:
                payload['today_is_working_day'] = 1
            else:
                payload['today_is_working_day'] = 0

            if all_data:
                area_data_dict = all_data[0]
                payload['num_found'] = area_data_dict['num_found']
                payload['total_structures'] = \
                    area_data_dict['total_structures']
                payload['found_coverage'] = \
                    int(area_data_dict['found_coverage'])
                payload['spray_coverage'] = \
                    int(area_data_dict['spray_coverage'])
                payload['spray_effectiveness'] = \
                    int(area_data_dict['spray_efectiveness'])
                payload['target_area_id'] = area_data_dict['target_area_id']
                payload['target_area_name'] = \
                    area_data_dict['target_area_name']
                payload['rhc_id'] = area_data_dict['rhc_id']
                payload['rhc_name'] = area_data_dict['rhc_name']
                payload['district_id'] = area_data_dict['district_id']
                payload['district_name'] = area_data_dict['district_name']
                payload['date'] = spray_date
            else:
                payload['num_found'] = 0
                payload['total_structures'] = target_area.parent.structures
                payload['found_coverage'] = 0
                payload['spray_coverage'] = 0
                payload['spray_effectiveness'] = 0
                payload['target_area_id'] = target_area.id
                payload['target_area_name'] = target_area.name
                payload['rhc_id'] = target_area.parent.id
                payload['rhc_name'] = target_area.parent.name
                payload['district_id'] = district_id
                payload['district_name'] = this_district.name
                payload['date'] = spray_date

            start_flow(flow_uuid, payload)


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
        start_flow(flow_uuid, payload)




