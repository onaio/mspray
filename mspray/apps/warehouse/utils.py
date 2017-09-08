import requests

from django.core.paginator import Paginator

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.serializers import mSpraySerializer


def chunked_iterator(queryset, chunk_size=500):
    paginator = Paginator(queryset, chunk_size)
    for page in range(1, paginator.num_pages + 1):
        yield paginator.page(page).object_list


def populate_druid_from_db():
    """
    Goes through the Database and populates Druid
    mainly used for testing druid with mspray data
    """
    url = "http://10.20.25.56:8200/v1/post/mspray"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    for submissions in chunked_iterator(
            SprayDay.objects.all().order_by('spray_date')):
        data = mSpraySerializer(submissions, many=True).data
        json_data = JSONRenderer().render(data)
        r = requests.post(url, data=json_data, headers=headers)
        print(r.text)
        print('\n')


def create_json_file(filename):
    """
    Goes through the Database and outputs submissions into a json file
    that can be imported into druid
    """
    for submissions in chunked_iterator(
            SprayDay.objects.all().order_by('spray_date')):
        data = mSpraySerializer(submissions, many=True).data
        lines = [JSONRenderer().render(dd) for dd in data]
        with open(filename, "ab") as fff:
            fff.write(b'\n'.join(lines))
