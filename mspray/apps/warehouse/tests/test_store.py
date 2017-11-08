from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.store import get_intervals


class TestStore(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self._load_fixtures()

    def test_get_intervals(self):
        """ test that we get the right intervals back """
        queryset = SprayDay.objects.all()
        first = queryset.first().data['_submission_time']
        last = queryset.last().data['_submission_time']
        expected = "{}/{}".format(first, last)
        self.assertEqual(expected, get_intervals(queryset))
