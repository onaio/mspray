# -*- coding=utf-8 -*-
"""
Ona API access util functions
"""
import json
from urllib.parse import urljoin

from django.conf import settings

import requests
from requests.auth import HTTPDigestAuth

ATTACHMENTS_KEY = "_attachments"
ONA_URI = getattr(settings, "ONA_URI", "https://api.ona.io")
ONA_TOKEN = getattr(settings, "ONA_API_TOKEN", "")


def fetch_osm_xml_data(data, xform_id=None):
    """Returns OSM XML data downloaded from a specific submission and form.
    """
    data_id = data.get("_id")
    _xform_id = xform_id
    if not _xform_id:
        _xform_id = data.get("_xform_id", 141279)

    url = urljoin(ONA_URI, "/api/v1/data/%s/%s.osm" % (_xform_id, data_id))
    headers = {"Authorization": "Token {}".format(ONA_TOKEN)}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content

    return None


def fetch_osm_xml(data, osm_filename=None):
    """
    Fetch OSM file for a given data from Ona API.
    """
    xml = None
    if ATTACHMENTS_KEY in data:
        attachments = data[ATTACHMENTS_KEY]
        if osm_filename:
            attachments = [
                a
                for a in attachments
                if a.get("filename").endswith(osm_filename)
            ]
            if not attachments:
                # pick wherever we get
                attachments = data[ATTACHMENTS_KEY]
        for attachment in attachments:
            filename = attachment.get("filename")
            is_osm_file = (
                attachment.get("mimetype") == "text/xml"
                and filename
                and filename.endswith("osm")
            )
            if is_osm_file:
                url = urljoin(ONA_URI, attachment.get("download_url"))
                response = requests.get(url)
                if response.status_code == 200:
                    xml = response.content
                    break

    return xml


def fetch_form_data(  # pylint: disable=too-many-arguments
    formid,  # pylint: disable=bad-continuation
    latest=None,  # pylint: disable=bad-continuation
    dataid=None,  # pylint: disable=bad-continuation
    dataids_only=False,  # pylint: disable=bad-continuation
    edited_only=False,  # pylint: disable=bad-continuation
    query=None,  # pylint: disable=bad-continuation
):
    """Fetch submission data from Ona API data endpoint.

    Keyword arguments:
    latest -- fetch only recent records.
    dataid -- fetch a record with the matching dataid
    dataids_only -- fetch only record ids.
    edited_only -- fetch only the records that have been edited
    query -- apply a specific query when fetching records.
    """
    query_params = None
    if latest:
        query_params = {"query": '{"_id":{"$gte":%s}}' % (latest)}
    if dataids_only:
        query_params = {} if query_params is None else query_params
        query_params["fields"] = '["_id"]'
    if edited_only:
        query_params = {"query": '{"_edited":"true"}'}

    if query:
        if query_params and "query" in query_params:
            _query = json.loads(query_params["query"])
            if isinstance(_query, dict):
                _query.update(query)
                query_params["query"] = json.dumps(_query)
        else:
            query_params = {"query": json.dumps(query)}

    if dataid is not None:
        url = urljoin(
            ONA_URI, "/api/v1/data/{}/{}.json".format(formid, dataid)
        )
    else:
        url = urljoin(ONA_URI, "/api/v1/data/{}.json".format(formid))
    headers = {"Authorization": "Token {}".format(ONA_TOKEN)}
    response = requests.get(url, headers=headers, params=query_params)

    return response.json() if response.status_code == 200 else None


def fetch_form(formid):
    """
    Fetch Ona Form.
    """
    headers = {"Authorization": "Token {}".format(ONA_TOKEN)}
    url = urljoin(ONA_URI, "/api/v1/forms/{}.json".format(formid))
    response = requests.get(url, headers=headers)

    return response.json() if response.status_code == 200 else None


def login(username, password):
    """
    Login with Ona Credetials
    """
    auth = HTTPDigestAuth(username, password)
    url = urljoin(ONA_URI, "/api/v1/user.json")
    response = requests.get(url, auth=auth)

    return response.json() if response.status_code == 200 else None
