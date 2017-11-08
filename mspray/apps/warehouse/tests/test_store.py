from unittest.mock import patch
from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.store import get_intervals, get_data, get_queryset


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

    def test_get_queryset(self):
        """
        test that get_queryset works
        """
        earliest = SprayDay.objects.order_by('created_on').first().created_on
        dt = timezone.now() - earliest
        minutes = dt.total_seconds() / 60
        x_minutes_ago = timezone.now() - timedelta(minutes=minutes)
        queryset = SprayDay.objects.filter(
                        created_on__gte=x_minutes_ago).order_by('created_on')
        queryset2 = get_queryset(minutes)
        self.assertTrue(queryset.count() > 0)
        self.assertEqual(queryset.count(), queryset2.count())

    @patch('mspray.apps.warehouse.store.ingest_sprayday')
    @patch('mspray.apps.warehouse.store.create_sprayday_druid_json_file')
    @patch('mspray.apps.warehouse.store.get_queryset')
    def test_get_data(self, queryset_mock, json_file_mock, ingest_mock):
        """
        Test that we store data by calling create_sprayday_druid_json_file
        and then we post it to Druid for indexing by calling ingest_sprayday
        with the right args
        """
        earliest = SprayDay.objects.order_by('created_on').first().created_on
        dt = timezone.now() - earliest
        minutes = dt.total_seconds() / 60
        queryset = SprayDay.objects.all()
        queryset_mock.return_value = queryset
        json_file_mock.return_value = "filename.json"
        get_data(minutes=minutes)
        self.assertTrue(queryset_mock.called)
        self.assertTrue(json_file_mock.called)
        self.assertTrue(ingest_mock.called)
        args, kwargs = ingest_mock.call_args_list[0]
        self.assertEqual(args[0], settings.AWS_S3_BASE_URL + "filename.json")
        self.assertEqual(kwargs['intervals'], get_intervals(queryset))
