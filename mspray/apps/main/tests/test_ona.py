# -*- coding=utf-8 -*-
"""
Test ona module
"""
import json

import requests
from django.test import TestCase
from httmock import HTTMock, urlmatch

from mspray.apps.main.ona import fetch_form_data, fetch_osm_xml

# pylint: disable=line-too-long
OSMXML = """<?xml version='1.0' encoding='UTF-8' ?><osm version="0.6" generator="OpenMapKit 0.7" user="theoutpost"><node id="-1943" lat="-11.202901601" lon="28.883830387" /><node id="-1946" lat="-11.202926082" lon="28.883944473" /><node id="-1945" lat="-11.202845645" lon="28.88396943" /><node id="-1944" lat="-11.202821164" lon="28.883858908" /><node id="-1943" lat="-11.202901601" lon="28.883830387" /><way id="-1942" action="modify"><nd ref="-1943" /><nd ref="-1946" /><nd ref="-1945" /><nd ref="-1944" /><nd ref="-1943" /><tag k="Shape_Area" v="0.00000000969" /><tag k="district_1" v="Mansa" /><tag k="manual_c_1" v="Targeted" /><tag k="OBJECTID" v="79621" /><tag k="rank_1" v="300.000000" /><tag k="province_1" v="Luapula" /><tag k="Shape_Leng" v="0.00039944548" /><tag k="psa_id_1" v="300 / 450" /><tag k="y" v="-11.20287380280" /><tag k="x3" v="28.88390064920" /><tag k="structur_1" v="450.000000" /><tag k="id" v="300 / 450_Mansa" /><tag k="spray_status" v="yes" /></way></osm>"""  # noqa
SUBMISSION_DATA = [{
    "osm_building": "OSMWay-1760.osm",
    "_id": 3563261,
    "_attachments": [{
        "mimetype": "text/xml",
        "download_url": "/api/v1/files/583377?filename=osm_experiments/attachments/OSMWay-1942.osm",  # noqa
        "filename": "osm_experiments/attachments/OSMWay-1942.osm",
        "instance": 3542171,
        "id": 583377,
        "xform": 79639
    }],
    "meta/instanceID": "uuid:da51a5c9-e87d-49df-9559-43f670f2079b"
}]


@urlmatch(netloc=r'(.*\.)?ona\.io$')
def onaio_osm_mock(url, request):  # pylint: disable=unused-argument
    """
    Mock Ona OSM response
    """
    response = requests.Response()
    response.status_code = 200
    # pylint: disable=protected-access
    response._content = OSMXML.strip().encode()

    return response


@urlmatch(netloc=r'(.*\.)?ona\.io$')
def onaio_json_mock(url, request):  # pylint: disable=unused-argument
    """
    Mock Ona data from API.
    """
    response = requests.Response()
    response.status_code = 200
    # pylint: disable=protected-access
    response._content = json.dumps(SUBMISSION_DATA).encode()

    return response


class TestOna(TestCase):
    """
    Test ona util functions.
    """
    def test_fetch_osm_xml(self):
        """
        Test fetch_osm_xml.
        """
        with HTTMock(onaio_osm_mock):
            xml = fetch_osm_xml(SUBMISSION_DATA[0])
            if isinstance(xml, str):
                xml = xml.encode()
            self.assertEqual(xml, OSMXML.strip().encode())

    def test_fetch_form_data(self):
        """
        Test fetch_form_data.
        """
        with HTTMock(onaio_json_mock):
            data = fetch_form_data(3563261)
            self.assertEqual(SUBMISSION_DATA[0], data[0])

            data = fetch_form_data(3563261, 3563260)
            self.assertEqual(SUBMISSION_DATA[0], data[0])
