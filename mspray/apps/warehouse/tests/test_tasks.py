from unittest.mock import patch

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.tasks import stream_to_druid
from mspray.celery import app


class TestTasks(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self._load_fixtures()

    @patch('mspray.apps.warehouse.tasks.send_to_tranquility')
    @patch('mspray.apps.warehouse.stream.send_request')
    def test_stream_to_druid(self, mock, mock2):
        """
        Test that stream_to_druid calls send_to_tranquility with the right arg
        """
        sprayday = SprayDay.objects.first()
        stream_to_druid.delay(sprayday.id)
        self.assertTrue(mock2.called)
        args, kwargs = mock2.call_args_list[0]
        self.assertEqual(args[0], sprayday)
