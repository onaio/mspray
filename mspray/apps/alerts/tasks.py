from django.conf import settings
from mspray.apps.warehouse.druid import get_druid_data
from mspray.apps.alerts.rapidpro import start_flow


def daily_spray_success_by_spray_area(district_id, spray_date):
    """
    Gets spray success rates for all the spray areas in a district, for a
    specific date.  If data is found, prepares a payload and sends it to
    RapidPro

    spray_date format == 2016-10-15
    """
    dimensions = ['target_area_id', 'target_area_name',
                  'target_area_structures', 'rhc_id', 'rhc_name',
                  'district_id', 'district_name']
    filters = dict(district_id=district_id, spray_date=spray_date)
    data, _ = get_druid_data(dimensions, filters)
    if data:
        flow_uuid = settings.RAPIDPRO_DAILY_SPRAY_SUCCESS_FLOW_UUID
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
                total_structures=item['total_structures'],
                date=spray_date
            )
            start_flow(flow_uuid, payload)
