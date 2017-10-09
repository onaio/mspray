from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.alerts.serializers import UserDistanceSerializer
from mspray.apps.alerts.tasks import user_distance

from httmock import HTTMock


class TestTasks(TestBase):

    def test_user_distance(self):
        self._load_fixtures()

        with HTTMock():
            sprayday = SprayDay.objects.first()
            data = UserDistanceSerializer(sprayday).data
            flow = user_distance(sprayday.id)
            self.assertTrue(isinstance(flow, object))
            # the 'extra' parameter on the flow is the data we sent it
            # but some key values are string-ified e.g. None becomes 'None'
            # so we test that the dicts have the same keys
            self.assertEqual(data.keys(), flow.extra.keys())
