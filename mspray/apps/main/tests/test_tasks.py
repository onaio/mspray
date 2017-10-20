from httmock import urlmatch, HTTMock
from unittest.mock import patch

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.main.tasks import link_spraypoint_with_osm
from mspray.apps.main.tasks import run_tasks_after_spray_data
from mspray.apps.main.utils import add_spray_data
from mspray.celery import app

OSMXML = """<?xml version='1.0' encoding='UTF-8' ?><osm version="0.6" generator="OpenMapKit 0.7" user="theoutpost"><node id="-1943" lat="-11.202901601" lon="28.883830387" /><node id="-1946" lat="-11.202926082" lon="28.883944473" /><node id="-1945" lat="-11.202845645" lon="28.88396943" /><node id="-1944" lat="-11.202821164" lon="28.883858908" /><node id="-1943" lat="-11.202901601" lon="28.883830387" /><way id="-1942" action="modify"><nd ref="-1943" /><nd ref="-1946" /><nd ref="-1945" /><nd ref="-1944" /><nd ref="-1943" /><tag k="Shape_Area" v="0.00000000969" /><tag k="district_1" v="Mansa" /><tag k="manual_c_1" v="Targeted" /><tag k="OBJECTID" v="79621" /><tag k="rank_1" v="300.000000" /><tag k="province_1" v="Luapula" /><tag k="Shape_Leng" v="0.00039944548" /><tag k="psa_id_1" v="300 / 450" /><tag k="y" v="-11.20287380280" /><tag k="x3" v="28.88390064920" /><tag k="structur_1" v="450.000000" /><tag k="id" v="300 / 450_Mansa" /><tag k="spray_status" v="yes" /></way></osm>"""  # noqa
SUBMISSION_DATA = {
    "today": "2015-09-16",
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
}


@urlmatch(netloc=r'(.*\.)?ona\.io$')
def onaio_mock(url, request):
    return OSMXML.strip()


class TestTasks(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_link_spraypoint_with_osm(self):
        sp = add_spray_data(SUBMISSION_DATA)

        with HTTMock(onaio_mock):
            link_spraypoint_with_osm(sp.pk)
            sp = SprayDay.objects.get(pk=sp.pk)
            self.assertTrue(sp.location is not None)

    @patch('mspray.apps.main.tasks.user_distance')
    @patch('mspray.apps.main.tasks.no_gps')
    @patch('mspray.apps.main.tasks.stream_to_druid')
    def test_run_tasks_after_spray_data(self, druid_mock, gps_mock,
                                        distance_mock):
        """
        Test that when run_tasks_after_spray_data is called, it starts all the
        tasks within:
            no_gps
            user_distance
            stream_to_druid
        """
        self._load_fixtures()
        sprayday = SprayDay.objects.first()
        run_tasks_after_spray_data(sprayday)
        self.assertTrue(druid_mock.delay.called)
        self.assertTrue(gps_mock.delay.called)
        self.assertTrue(distance_mock.delay.called)
