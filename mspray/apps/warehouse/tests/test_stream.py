from unittest.mock import patch

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.stream import send_to_tranquility
from mspray.apps.warehouse.stream import get_mspray_stream_url
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer


class TestStream(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self._load_fixtures()

    @patch('mspray.apps.warehouse.stream.send_request')
    def test_send_to_tranquility(self, mock):
        """
        Test that send_to_tranquility sends a request with the expected data
        """
        sprayday = SprayDay.objects.first()
        sprayday_data = SprayDayDruidSerializer(sprayday).data
        sprayday_json = JSONRenderer().render(sprayday_data)
        send_to_tranquility(sprayday)
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0], sprayday_json)
        self.assertEqual(args[1], get_mspray_stream_url())

    def test_get_mspray_stream_url(self):
        """ test that we construct the full trabquility url successfully """
        with self.settings(DRUID_SPRAYDAY_TRANQUILITY_URI='http://127.0.0.1',
                           DRUID_SPRAYDAY_TRANQUILITY_PORT=8200,
                           DRUID_SPRAYDAY_TRANQUILITY_PATH='/v1/post/mspray'):
            self.assertEqual(get_mspray_stream_url(),
                             'http://127.0.0.1:8200/v1/post/mspray')
