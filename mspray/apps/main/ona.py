import requests
from urllib.parse import urljoin

from django.conf import settings


ATTACHMENTS_KEY = '_attachments'
ONA_URI = getattr(settings, 'ONA_URI', 'https://ona.io')
ONA_TOKEN = getattr(settings, 'ONA_API_TOKEN', '')


def fetch_osm_xml(data):
    xml = None
    if ATTACHMENTS_KEY in data:
        for attachment in data[ATTACHMENTS_KEY]:
            filename = attachment.get('filename')
            if attachment.get('mimetype') == 'text/xml' and \
                    filename.endswith('osm'):
                url = urljoin(ONA_URI, attachment.get('download_url'))
                response = requests.get(url)
                if response.status_code == 200:
                    xml = response.content
                    break

    return xml


def fetch_form_data(formid):
    url = urljoin(ONA_URI, '/api/v1/data/{}.json'.format(formid))
    headers = {
        'Authorization': 'Token {}'.format(ONA_TOKEN)
    }
    data = None
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()

    return data
