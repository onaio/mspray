from decimal import Decimal, InvalidOperation

from pydruid.client import PyDruid
from pydruid.utils import aggregators
from pydruid.utils import filters
from pydruid.utils.postaggregator import Field

from django.conf import settings


def calculate_rhc_totals(totals):
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
        totals['spray_efectiveness'] = (total_sprayed /
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


def get_rhc_data(pk=None, dimensions=None):
    query = PyDruid(settings.DRUID_BROKER_URI, 'druid/v2')
    params = dict(
        datasource='mspraytest',
        granularity='all',
        intervals='1917-09-08T00:00:00+00:00/2017-09-08T10:41:37+00:00',
        aggregations={
            'num_not_sprayable': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('sprayable') == 'no']
                ),
                aggregators.longsum('count')
            ),
            'num_not_sprayed': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('sprayable') == 'yes',
                            filters.Dimension('sprayed') == 'no']
                ),
                aggregators.longsum('count')
            ),
            'num_sprayed': aggregators.filtered(
                filters.Dimension('sprayed') == 'yes',
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
                            filters.Dimension('sprayed') == 'yes']
                ),
                aggregators.longsum('count')
            ),
            'num_not_sprayed_no_duplicates': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'false',
                            filters.Dimension('sprayable') == 'yes',
                            filters.Dimension('sprayed') == 'no']
                ),
                aggregators.longsum('count')
            ),
            'num_sprayed_duplicates': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'true',
                            filters.Dimension('sprayable') == 'yes',
                            filters.Dimension('sprayed') == 'yes']
                ),
                aggregators.longsum('count')
            ),
            'num_not_sprayable_no_duplicates': aggregators.filtered(
                filters.Filter(
                    type='and',
                    fields=[filters.Dimension('is_duplicate') == 'false',
                            filters.Dimension('sprayable') == 'no']
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
            "columns": ["target_area_name"]
        }
    )
    if pk:
        params['filter'] = (filters.Dimension('rhc_id') == pk)
    if dimensions is None:
        params['dimensions'] = ['target_area_id', 'target_area_name',
                                'target_area_structures']
    else:
        params['dimensions'] = dimensions

    try:
        request = query.groupby(**params)
    except OSError:
        pass
    else:
        result = request.result
        data = [x['event'] for x in result if x['event']['target_area_id']
                is not None]
        total_structures, total_found, total_sprayed = Decimal(0), Decimal(0),\
            Decimal(0)
        for d in data:
            d['total_structures'] = int(d['target_area_structures']) +\
                d['num_new_no_duplicates'] + d['num_sprayed_duplicates'] -\
                d['num_not_sprayable_no_duplicates']
            try:
                found_coverage = (Decimal(d['num_found']) /
                                  Decimal(d['total_structures'])) * 100
            except ZeroDivisionError:
                found_coverage = 0
            except InvalidOperation:
                found_coverage = 0
            try:
                spray_efectiveness = (Decimal(d['num_sprayed']) /
                                      Decimal(d['total_structures'])) *\
                    Decimal(100)
            except ZeroDivisionError:
                spray_efectiveness = 0
            except InvalidOperation:
                found_coverage = 0
            try:
                spray_coverage = (Decimal(d['num_sprayed']) /
                                  Decimal(d['num_found'])) *\
                    Decimal(100)
            except ZeroDivisionError:
                spray_coverage = 0
            except InvalidOperation:
                found_coverage = 0
            d['spray_efectiveness'] = spray_efectiveness
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
            'spray_efectiveness': Decimal(0),
            'spray_coverage': Decimal(0),
        }
        return data, totals
    return [], {}
