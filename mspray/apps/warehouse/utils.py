import operator

from django.core.paginator import Paginator
from django.conf import settings

from mspray.apps.warehouse.druid import druid_simple_groupby


def chunked_iterator(queryset, chunk_size=500):
    paginator = Paginator(queryset, chunk_size)
    for page in range(1, paginator.num_pages + 1):
        yield paginator.page(page).object_list


def get_duplicates(ta_pk=None, sprayed=True):
    dimensions = ["osmid"]
    filters = [['is_duplicate', operator.eq, "true"]]
    if sprayed is True:
        filters.append(['sprayed', operator.eq,
                       settings.MSPRAY_WAS_SPRAYED_VALUE])
    else:
        filters.append(['sprayed', operator.eq,
                       settings.MSPRAY_WAS_NOT_SPRAYED_VALUE])
    if ta_pk:
        filters.append(['target_area_id', operator.eq, ta_pk])
    data = druid_simple_groupby(dimensions, filters)
    return [x['event'] for x in data if x['event']['osmid'] is not None]


def flatten(d, parent_key=''):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s__' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)
