from unittest.mock import patch

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.main.tasks import link_spraypoint_with_osm
from mspray.apps.main.tasks import run_tasks_after_spray_data
from mspray.apps.main.utils import add_spray_data
from mspray.celery import app


OSMXML = """
    <?xml version='1.0' encoding='UTF-8' ?>
    <osm version="0.6" generator="OpenMapKit Android 1.1.16-ona" user="">
    <node id="-41351" timestamp="2017-10-04T20:03:35Z" user=""
    lat="-15.4189358" lon="28.3545641" /><node id="-41356"
    timestamp="2017-10-04T20:03:35Z" user="" lat="-15.4190764"
    lon="28.3547381" /><node id="-41357" timestamp="2017-10-04T20:03:35Z"
    user="" lat="-15.4191478" lon="28.3546759" /><node id="-41358"
    timestamp="2017-10-04T20:03:35Z" user="" lat="-15.4191416"
    lon="28.3546682" /><node id="-41359" timestamp="2017-10-04T20:03:35Z"
    user="" lat="-15.4191617" lon="28.3546507" /><node id="-41360"
    timestamp="2017-10-04T20:03:35Z" user="" lat="-15.4191244"
    lon="28.3546046" /><node id="-41361" timestamp="2017-10-04T20:03:35Z"
    user="" lat="-15.4191049" lon="28.3546216" /><node id="-41362"
    timestamp="2017-10-04T20:03:35Z" user="" lat="-15.4190864"
    lon="28.3545987" /><node id="-41363" timestamp="2017-10-04T20:03:35Z"
    user="" lat="-15.4191126" lon="28.3545759" /><node id="-41364"
    timestamp="2017-10-04T20:03:35Z" user="" lat="-15.4190536"
    lon="28.3545031" /><node id="-41365" timestamp="2017-10-04T20:03:35Z"
    user="" lat="-15.4190285" lon="28.354525" /><node id="-41366"
    timestamp="2017-10-04T20:03:35Z" user="" lat="-15.4190087"
    lon="28.3545006" /><node id="-41351" timestamp="2017-10-04T20:03:35Z"
    user="" lat="-15.4189358" lon="28.3545641" /><way id="-41367"
    action="modify" timestamp="2017-10-04T20:03:35Z" user=""><nd ref="-41351"
    /><nd ref="-41356" /><nd ref="-41357" /><nd ref="-41358" />
    <nd ref="-41359" /><nd ref="-41360" /><nd ref="-41361" />
    <nd ref="-41362" /><nd ref="-41363" /><nd ref="-41364" />
    <nd ref="-41365" /><nd ref="-41366" /><nd ref="-41351" />
    <tag k="building" v="residential" /><tag k="osm_way_id" v="528511977" />
    <tag k="spray_status" v="notsprayed" /><tag k="notsprayed_reason"
    v="sick" /></way></osm>
"""

SUBMISSION_DATA = {
    'tla_leader': '99101', '_tags': [], '_media_count': 1, '_id': 3563261,
    'sprayable/unsprayed/population/unsprayed_pregnant_women': '0',
    'today': '2017-10-04', 'imei': '353750066007314',
    'sprayable/unsprayed/population/unsprayed_children_u5': '0',
    'sprayable/sprayop_name': '99209', 'osmstructure:way:id': '-41367',
    'start': '2017-10-04T22:03:13.238+02', '_status': 'submitted_via_web',
    'spray_area': 'test5.99', '_edited': False, '_version': '20170927',
    'meta/instanceID': 'uuid:30d11f1e-39f2-40b2-b3b0-201b6e043bc2',
    'deviceid': '353750066007314', '_geolocation': [None, None],
    '_uuid': '30d11f1e-39f2-40b2-b3b0-201b6e043bc2',
    'formhub/uuid': 'fbe6a176b1494b608c683ca27f3599db',
    'sprayable/unsprayed/population/unsprayed_nets': '0',
    '_submission_time': '2017-10-04T20:06:35',
    'sprayable/unsprayed/unsprayed_totalpop': '4',
    'sprayformid': '04.10.99209', 'health_facility': '202',
    'sprayable/unsprayed/unsprayed_females': 2,
    '_notes': [], 'sprayable/unsprayed/population/unsprayed_roomsfound': 2,
    '_xform_id_string': 'Zambia_2017IRS_HH', '_xform_id': 244266,
    'sprayable/sprayop_code': '99209',
    'sprayable/structure_head_name': 'H3', '_submitted_by': 'msprayzambia2017',
    'sprayable/unsprayed/reason': 'L',
    'values_from_omk/spray_status': 'notsprayed', 'supervisor_name': '99402',
    'sprayable/irs_card_num': '12345678', '_total_media': 0,
    "_id": 3563261,
    '_attachments': [
        {
            'filename': 'akros_health/attachments/'
                        '1410dd5377f692456ab1a1515786f1045189ca8e.osm',
            'download_url': '/api/v1/files/5551567?filename=akros_health'
                            '/attachments/'
                            '1410dd5377f692456ab1a1515786f1045189ca8e.osm',
            'id': 5551567, "mimetype": "text/xml",
        }
    ],

}


class TestTasks(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    @patch('mspray.apps.main.tasks.fetch_osm_xml')
    def test_link_spraypoint_with_osm(self, mock):
        """
        Test that we can successfully link spraypoint wiht osm
        """
        self._load_fixtures()
        mock.return_value = OSMXML.strip()
        sp = add_spray_data(SUBMISSION_DATA)
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
        druid_args, druid_kwargs = druid_mock.delay.call_args_list[0]
        gps_args, gps_kwargs = gps_mock.delay.call_args_list[0]
        distance_args, distance_kwargs = distance_mock.delay.call_args_list[0]
        self.assertEqual(druid_args[0], sprayday.id)
        self.assertEqual(gps_args[0], sprayday.id)
        self.assertEqual(distance_args[0], sprayday.id)
