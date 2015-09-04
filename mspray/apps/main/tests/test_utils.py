from django.test import TestCase

from mspray.apps.main.utils import avg_time_tuple
from mspray.apps.main.utils import avg_time_per_group


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
