from unittest.mock import patch

from django.conf import settings

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.main.models.spray_day import DATA_ID_FIELD
from mspray.apps.main.utils import add_spray_data
from mspray.apps.main.utils import avg_time_tuple
from mspray.apps.main.utils import avg_time_per_group
from mspray.celery import app

SUBMISSION_DATA = [{
    "osm_building": "OSMWay-1760.osm",
    "today": "2015-09-21",
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


class TestUtils(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_avg_time_tuple(self):
        times = [(15, 21), (15, 11), (8, 47)]
        self.assertEqual(avg_time_tuple(times), (13, 6))
        times = [(23, 57), (3, 24), (2, 39)]
        self.assertEqual(avg_time_tuple(times), (10, 0))
        times = [(15, 18), (18, 35), (11, 26)]
        self.assertEqual(avg_time_tuple(times), (15, 6))

    def test_avg_time_per_so(self):
        results = [
            ('SOP0483', '2015-09-01', 12.0, 59.0),
            ('SOP0483', '2015-09-02', 15.0, 34.0),
            ('SOP0483', '2015-09-03', 11.0, 57.0),
            ('SOP0484', '2015-09-01', 13.0, 57.0),
            ('SOP0484', '2015-09-02', 15.0, 46.0),
            ('SOP0484', '2015-09-03', 14.0, 15.0),
            ('SOP0485', '2015-09-01', 12.0, 30.0),
            ('SOP0485', '2015-09-02', 15.0, 51.0),
            ('SOP0485', '2015-09-03', 12.0, 20.0)
        ]

        self.assertEqual(avg_time_per_group(results), (13, 54))
        self.assertEqual(avg_time_per_group([]), (None, None))

    def test_add_spray_data(self):
        count = SprayDay.objects.count()
        add_spray_data(SUBMISSION_DATA[0])
        self.assertTrue(SprayDay.objects.count() > count)

    @patch('mspray.apps.main.utils.run_tasks_after_spray_data')
    def test_add_spray_data_with_osm(self, mock):
        """
        Test that add_spray_data createsa SprayDay object and that if it has
        OSM data it runs run_tasks_after_spray_data
        """
        self._load_fixtures()
        # get submission data that has OSM info
        sp = SprayDay.objects.filter(
                data__has_key=settings.MSPRAY_OSM_PRESENCE_FIELD).first()
        data = sp.data
        # change the _id field so that we can reuse this data
        data[DATA_ID_FIELD] = 111
        count = SprayDay.objects.count()
        sp = add_spray_data(data)
        self.assertTrue(SprayDay.objects.count() > count)
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0], sp)
