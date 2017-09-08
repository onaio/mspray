from decimal import Decimal

from pydruid.client import PyDruid
from pydruid.utils import aggregators
from pydruid.utils import filters

from django.conf import settings


def get_rhc_data(pk):
    query = PyDruid(settings.DRUID_BROKER_URI, 'druid/v2')
    try:
        request = query.groupby(
            datasource='mspraytest',
            granularity='all',
            dimensions=['target_area_id', 'target_area_name',
                        'target_area_structures'],
            intervals='1917-09-08T00:00:00+00:00/2017-09-08T10:41:37+00:00',
            filter=(filters.Dimension('rhc_id') == pk),
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
            },
            limit_spec={
                "type": "default",
                "limit": 50000,
                "columns": ["target_area_name"]
            }
        )
    except OSError:
        pass
    else:
        result = request.result
        data = [x['event'] for x in result]
        for d in data:
            found = d['num_sprayed_no_duplicates'] + d['num_duplicate']
            found_coverage = (d['num_sprayed'] / found) * 100
            sprayable = found - d['num_not_sprayable']
            spray_efectiveness = (Decimal(d['num_sprayed']) /
                                  Decimal(sprayable)) * Decimal(100)
            spray_coverage = (Decimal(d['num_sprayed']) / Decimal(found)) *\
                Decimal(100)
            d['found'] = found
            d['spray_efectiveness'] = spray_efectiveness
            d['found_coverage'] = found_coverage
            d['spray_coverage'] = spray_coverage
        return data
    return []
