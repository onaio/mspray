import operator
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from json.decoder import JSONDecodeError

from django.conf import settings

from mspray.apps.warehouse.druid import druid_simple_groupby


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


def requests_retry_session(retries=3, backoff_factor=0.3,
                           status_forcelist=(500, 502, 504), session=None):
    """
    A wrapper around the requests module which retries failed connections
    https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def send_request(json, url):
    headers = {
        'Content-Type': 'application/json',
    }
    s = requests.Session()
    s.headers.update(headers)
    r = requests_retry_session(session=s).post(url, data=json)
    try:
        return r.json()
    except JSONDecodeError:
        return r.text
