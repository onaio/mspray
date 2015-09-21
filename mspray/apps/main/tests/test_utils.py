from django.test import TestCase

from mspray.apps.main.models import SprayDay
from mspray.apps.main.utils import add_spray_data
from mspray.apps.main.utils import avg_time_tuple
from mspray.apps.main.utils import avg_time_per_group

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


class TestUtils(TestCase):

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
