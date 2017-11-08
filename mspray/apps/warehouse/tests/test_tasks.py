from datetime import timedelta

from unittest.mock import patch

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.tasks import stream_to_druid, reload_druid_data
from mspray.apps.warehouse.tasks import reload_yesterday_druid_data
from mspray.celery import app
from django.utils import timezone


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
        stream_to_druid(sprayday.id)
        self.assertTrue(mock2.called)
        args, kwargs = mock2.call_args_list[0]
        self.assertEqual(args[0], sprayday)

    @patch('mspray.apps.warehouse.tasks.get_data')
    def test_reload_druid_data(self, mock):
        """
        Test that reload_druid_data calls get_data with the right argument
        """
        reload_druid_data(minutes=15)
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(15, kwargs['minutes'])

    @patch('mspray.apps.warehouse.tasks.get_historical_data')
    def test_reload_yesterday_druid_data(self, mock):
        """
        Test that reload_yesterday_druid_data actually calls
        get_historical_data with the right args
        """
        today = timezone.now()
        jana = today - timedelta(days=1)

        reload_yesterday_druid_data()
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(kwargs['day'], jana.day)
        self.assertEqual(kwargs['month'], jana.month)
        self.assertEqual(kwargs['year'], jana.year)
