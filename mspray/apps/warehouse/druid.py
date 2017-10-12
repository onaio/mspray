from decimal import Decimal, InvalidOperation

from pydruid.client import PyDruid
from pydruid.utils import aggregators
from pydruid.utils import filters
from pydruid.utils.postaggregator import Field

from django.conf import settings

from mspray.apps.main.models import Location


def get_target_area_totals(data):
    """
    Loops through data and calculates totals
    """
    total_structures, total_found, total_sprayed = Decimal(0), Decimal(0),\
        Decimal(0)
    for d in data:
        d['total_structures'] = int(d['target_area_structures']) +\
            d['num_new_no_duplicates'] + d['num_sprayed_duplicates'] -\
            d['num_not_sprayable_no_duplicates']

        d['num_not_visited'] = d['total_structures'] - d['num_found']

        try:
            found_coverage = (Decimal(d['num_found']) /
                              Decimal(d['total_structures'])) * 100
        except ZeroDivisionError:
            found_coverage = 0
        except InvalidOperation:
            found_coverage = 0

        try:
            spray_effectiveness = (Decimal(d['num_sprayed']) /
                                   Decimal(d['total_structures'])) *\
                Decimal(100)
        except ZeroDivisionError:
            spray_effectiveness = 0
        except InvalidOperation:
            spray_effectiveness = 0

        try:
            spray_coverage = (Decimal(d['num_sprayed']) /
                              Decimal(d['num_found'])) *\
                Decimal(100)
        except ZeroDivisionError:
            spray_coverage = 0
        except InvalidOperation:
            spray_coverage = 0

        d['spray_effectiveness'] = spray_effectiveness
        d['found_coverage'] = found_coverage
        d['spray_coverage'] = spray_coverage
        total_found += Decimal(d['num_found'])
        total_sprayed += Decimal(d['num_sprayed'])
        total_structures += Decimal(d['total_structures'])
    totals = {
        'found': total_found,
        'sprayed': total_sprayed,
        'structures': total_structures,
        'found_coverage': Decimal(0),
        'spray_effectiveness': Decimal(0),
        'spray_coverage': Decimal(0),
    }
    return totals


def calculate_target_area_totals(totals):
    """
    Takes a 'totals' dict and calculates the found, structures and sprayed
    indicatos
    """
    total_found = totals['found']
    total_structures = totals['structures']
    total_sprayed = totals['sprayed']
    try:
        totals['found_coverage'] = (total_found /
                                    total_structures) * 100
    except ZeroDivisionError:
        pass
    except InvalidOperation:
        pass
    try:
        totals['spray_effectiveness'] = (total_sprayed /
                                         total_structures) * 100
    except ZeroDivisionError:
        pass
    except InvalidOperation:
        pass
    try:
        totals['spray_coverage'] = (total_sprayed /
                                    total_found) * 100
    except ZeroDivisionError:
        pass
    except InvalidOperation:
        pass
    return totals


def process_location_data(location_dict, district_data):
    """
    Takes a group of target areas in a location and calculates location-wide
    indicators
    """
    result = {}
    if location_dict['level'] == 'district':
        target_areas = Location.objects.filter(
            parent__parent__id=location_dict['id']).filter(level='ta')
    elif location_dict['level'] == 'RHC':
        target_areas = Location.objects.filter(
            parent__id=location_dict['id']).filter(level='ta')
    else:
        target_areas = Location.objects.filter(
            id=location_dict['id']).filter(level='ta')
    target_area_count = target_areas.count()
    visited, sprayed = 0, 0
    for x in district_data:
        if x['found_coverage'] >= Decimal(20):
            visited += 1
        if x['spray_effectiveness'] >= Decimal(85):
            sprayed += 1
    result['target_area_count'] = target_area_count
    result['visited'] = visited
    result['sprayed'] = sprayed

    try:
        visited_percentage = (Decimal(visited) / Decimal(target_area_count)) *\
            Decimal(100)
    except ZeroDivisionError:
        visited_percentage = 0
    except InvalidOperation:
        visited_percentage = 0

    try:
        sprayed_percentage = (Decimal(sprayed) / Decimal(visited)) *\
            Decimal(100)
    except ZeroDivisionError:
        sprayed_percentage = 0
    except InvalidOperation:
        sprayed_percentage = 0

    try:
        sprayed_coverage = (Decimal(sprayed) / Decimal(target_area_count)) *\
            Decimal(100)
    except ZeroDivisionError:
        sprayed_coverage = 0
    except InvalidOperation:
        sprayed_coverage = 0

    result['visited_percentage'] = visited_percentage
    result['sprayed_percentage'] = sprayed_percentage
    result['sprayed_coverage'] = sprayed_coverage
    return result


def process_druid_data(druid_data, extractor='target_area_id'):
    """
    Mainly computes 'target_area' totals of given druid data
    Inputs:
        extractor => field to use to get data from druid result
    """
    data, totals = [], {}
    data = [x['event'] for x in druid_data if x['event'][extractor]
            is not None]
    totals = get_target_area_totals(data)
    return data, totals


def get_druid_data(dimensions=None, filter_list=[], filter_type="and",
                   order_by=["target_area_name"],
                   datasource=settings.DRUID_SPRAYDAY_DATASOURCE):
    """
    Runs a query against Druid, returns data with metrics
    Inputs:
        dimensions => list of dimensions to group by
        filter_list => list of list of things to filter with e.g.
                        filter_list=[['target_area_id', operator.ne, 1],
                                     ['sprayable', operator.eq, "true"],
                                     ['dimension', operator, "value"]])
        filter_type => type of Druid filter to perform,
        order_by => field(s) to order the data by
    """
    query = PyDruid(settings.DRUID_BROKER_URI, 'druid/v2')
    params = dict(
        datasource=datasource,
        granularity='all',
        intervals=settings.DRUID_INTERVAL,
        aggregations={
            'num_not_sprayable': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('sprayable') == 'false']
                ),
                aggregators.longsum('count')
            ),
            'num_not_sprayed': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('sprayable') == 'true',
                            filters.Dimension('sprayed') ==
                            settings.MSPRAY_WAS_NOT_SPRAYED_VALUE]
                ),
                aggregators.longsum('count')
            ),
            'num_sprayed': aggregators.filtered(
                filters.Dimension('sprayed') ==
                settings.MSPRAY_WAS_SPRAYED_VALUE,
                aggregators.longsum('count')
            ),
            'num_new': aggregators.filtered(
                filters.Dimension('is_new') == 'true',
                aggregators.longsum('count')
            ),
            'num_new_no_duplicates': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'false',
                            filters.Dimension('is_new') == 'true']
                ),
                aggregators.longsum('count')
            ),
            'num_duplicate': aggregators.filtered(
                filters.Dimension('is_duplicate') == 'true',
                aggregators.longsum('count')
            ),
            'num_sprayed_no_duplicates': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'false',
                            filters.Dimension('sprayed') ==
                            settings.MSPRAY_WAS_SPRAYED_VALUE]
                ),
                aggregators.longsum('count')
            ),
            'num_not_sprayed_no_duplicates': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'false',
                            filters.Dimension('sprayable') == 'true',
                            filters.Dimension('sprayed') ==
                            settings.MSPRAY_WAS_NOT_SPRAYED_VALUE]
                ),
                aggregators.longsum('count')
            ),
            'num_sprayed_duplicates': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'true',
                            filters.Dimension('sprayable') == 'true',
                            filters.Dimension('sprayed') ==
                            settings.MSPRAY_WAS_SPRAYED_VALUE]
                ),
                aggregators.longsum('count')
            ),
            'num_not_sprayable_no_duplicates': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'false',
                            filters.Dimension('sprayable') == 'false']
                ),
                aggregators.longsum('count')
            ),
            'num_refused': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'false',
                            filters.Dimension('is_refused') == 'true',
                            filters.Dimension('sprayed') ==
                            settings.MSPRAY_WAS_NOT_SPRAYED_VALUE]
                ),
                aggregators.longsum('count')
            ),
        },
        post_aggregations={
            'num_found': Field('num_sprayed_no_duplicates') +
            Field('num_sprayed_duplicates') +
            Field('num_not_sprayed_no_duplicates')
        },
        limit_spec={
            "type": "default",
            "limit": 50000,
            "columns": order_by
        }
    )
    if filter_list:
        fields = []
        for this_filter in filter_list:
            compare_dim = filters.Dimension(this_filter[0])
            comparison_operator = this_filter[1]  # e.g. operator.eq
            compare_dim_value = this_filter[2]
            fields.append(comparison_operator(compare_dim, compare_dim_value))
        params['filter'] = filters.Filter(
            type=filter_type,
            fields=fields
        )

    if dimensions is None:
        params['dimensions'] = ['target_area_id', 'target_area_name',
                                'target_area_structures']
    else:
        params['dimensions'] = dimensions

    try:
        request = query.groupby(**params)
    except OSError:
        return []
    else:
        return request.result


def druid_simple_groupby(dimensions, filter_list=[], filter_type="and",
                         datasource=settings.DRUID_SPRAYDAY_DATASOURCE):
    """
    Inputs:
        dimensions => list of dimensions to group by
        filter_list => list of list of things to filter with e.g.
                        filter_list=[['target_area_id', operator.ne, 1],
                                     ['sprayable', operator.eq, "true"],
                                     ['dimension', operator, "value"]])
        filter_type => type of Druid filter to perform
    """
    query = PyDruid(settings.DRUID_BROKER_URI, 'druid/v2')
    params = dict(
        datasource=datasource,
        granularity='all',
        intervals=settings.DRUID_INTERVAL,
        limit_spec={
            "type": "default",
            "limit": 50000,
        }
    )
    params['dimensions'] = dimensions
    if filter_list:
        fields = []
        for this_filter in filter_list:
            compare_dim = filters.Dimension(this_filter[0])
            comparison_operator = this_filter[1]  # e.g. operator.eq
            compare_dim_value = this_filter[2]
            fields.append(comparison_operator(compare_dim, compare_dim_value))
        params['filter'] = filters.Filter(
            type=filter_type,
            fields=fields
        )

    try:
        request = query.groupby(**params)
    except OSError:
        pass
    else:
        return request.result
    return []
