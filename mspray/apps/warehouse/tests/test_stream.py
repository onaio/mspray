from unittest.mock import patch

from rest_framework.renderers import JSONRenderer

from django.conf import settings

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.stream import send_to_tranquility
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer


class TestStream(TestBase):

    def setUp(self):
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
        self.assertEqual(args[1], settings.DRUID_SPRAYDAY_TRANQUILITY_URI)
