from mspray.apps.main.models import Location
from mspray.apps.main.query import get_location_qs


def get_district_summary_data():
    """
    Gets a queryset of Districts and serializes it
    """
    from mspray.apps.main.serializers.target_area import DistrictSerializer
    queryset = Location.objects.filter(level='district')
    queryset = get_location_qs(queryset).extra(select={
            "xmin": 'ST_xMin("main_location"."geom")',
            "ymin": 'ST_yMin("main_location"."geom")',
            "xmax": 'ST_xMax("main_location"."geom")',
            "ymax": 'ST_yMax("main_location"."geom")'
        }).values(
            'pk', 'code', 'level', 'name', 'parent', 'structures',
            'xmin', 'ymin', 'xmax', 'ymax', 'num_of_spray_areas',
            'num_new_structures', 'total_structures', 'visited', 'sprayed'
        )
    serialized = DistrictSerializer(queryset, many=True)
    return serialized.data


def get_district_summary_totals(district_list):
    """
    Takes a serialized list of districts and returns totals of certain fields
    """
    fields = ['structures', 'visited_total', 'visited_sprayed',
              'visited_not_sprayed', 'visited_refused', 'visited_other',
              'not_visited', 'found', 'num_of_spray_areas']
    totals = {}
    for rec in district_list:
        for field in fields:
            totals[field] = rec[field] + (totals[field]
                                          if field in totals else 0)
    return totals


def get_district_summary():
    """
    Returns a summary of spray effectiveness data for Districts
    Does not use Druid
    """
    district_list = get_district_summary_data()
    totals = get_district_summary_totals(district_list)
    return district_list, totals
