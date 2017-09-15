from django.core.paginator import Paginator

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.serializers import mSpraySerializer
from mspray.apps.warehouse.druid import druid_select_query


def chunked_iterator(queryset, chunk_size=500):
    paginator = Paginator(queryset, chunk_size)
    for page in range(1, paginator.num_pages + 1):
        yield paginator.page(page).object_list


def create_json_file(filename, queryset=None):
    """
    Goes through the Database and outputs submissions into a json file
    that can be imported into druid
    """
    if not queryset:
        queryset = SprayDay.objects.all().order_by('id')
    for submissions in chunked_iterator(queryset):
        data = mSpraySerializer(submissions, many=True).data
        lines = [JSONRenderer().render(dd) for dd in data]
        with open(filename, "ab") as fff:
            fff.write(b'\n'.join(lines))


def get_duplicates(ta_pk=None, sprayed=True):
    dimensions = ["osmid"]
    filters = {'is_duplicate': "true"}
    if sprayed is True:
        filters['sprayed'] = "yes"
    else:
        filters['sprayed'] = "no"
    if ta_pk:
        filters['target_area_id'] = ta_pk
    data = druid_select_query(dimensions, filters)
    return [x['event'] for x in data if x['event']['osmid'] is not None]
