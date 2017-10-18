# -*- coding=utf-8 -*-
"""
Ona API access util functions
"""
from urllib.parse import urljoin

from django.conf import settings

import requests
from requests.auth import HTTPDigestAuth

ATTACHMENTS_KEY = '_attachments'
ONA_URI = getattr(settings, 'ONA_URI', 'https://ona.io')
ONA_TOKEN = getattr(settings, 'ONA_API_TOKEN', '')


def fetch_osm_xml(data):
    """
    Fetch OSM file for a given data from Ona API.
    """
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


def fetch_form_data(formid, latest=None, dataid=None, dataids_only=False,
                    edited_only=False):
    """
    Fetch submission data from Ona API data endpoint.
    """
    query = None
    if latest:
        query = {'query': '{"_id":{"$gte":%s}}' % (latest)}
    if dataids_only:
        query = {} if query is None else query
        query['fields'] = '["_id"]'
    if edited_only:
        query = {'query': '{"_edited":"true"}'}

    if dataid is not None:
        url = urljoin(ONA_URI, '/api/v1/data/{}/{}.json'.format(
            formid, dataid))
    else:
        url = urljoin(ONA_URI, '/api/v1/data/{}.json'.format(formid))
    headers = {'Authorization': 'Token {}'.format(ONA_TOKEN)}
    response = requests.get(url, headers=headers, params=query)

    return response.json() if response.status_code == 200 else None


def fetch_form(formid):
    """
    Fetch Ona Form.
    """
    headers = {'Authorization': 'Token {}'.format(ONA_TOKEN)}
    url = urljoin(ONA_URI, '/api/v1/forms/{}.json'.format(formid))
    response = requests.get(url, headers=headers)

    return response.json() if response.status_code == 200 else None


def login(username, password):
    """
    Login with Ona Credetials
    """
    auth = HTTPDigestAuth(username, password)
    url = urljoin(ONA_URI, '/api/v1/user.json')
    response = requests.get(url, auth=auth)

    return response.json() if response.status_code == 200 else None
