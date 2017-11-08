import os

from unittest.mock import patch
from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer
from mspray.apps.main.utils import queryset_iterator
from mspray.apps.warehouse.store import get_druid_intervals, get_data
from mspray.apps.warehouse.store import get_historical_data
from mspray.apps.warehouse.store import create_sprayday_druid_json_file
from mspray.apps.warehouse.store import get_sprayday_queryset_from_x_minutes


class TestStore(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self._load_fixtures()

    def test_get_druid_intervals(self):
        """ test that we get the right intervals back """
        queryset = SprayDay.objects.all()
        first = queryset.first().data['_submission_time']
        last = queryset.last().data['_submission_time']
        expected = "{}/{}".format(first, last)
        self.assertEqual(expected, get_druid_intervals(queryset))

    def test_get_sprayday_queryset_from_x_minutes(self):
        """
        test that get_sprayday_queryset_from_x_minutes works
        """
        earliest = SprayDay.objects.order_by('created_on').first().created_on
        dt = timezone.now() - earliest
        minutes = dt.total_seconds() / 60
        x_minutes_ago = timezone.now() - timedelta(minutes=minutes)
        queryset = SprayDay.objects.filter(
                        created_on__gte=x_minutes_ago).order_by('created_on')
        queryset2 = get_sprayday_queryset_from_x_minutes(minutes)
        self.assertTrue(queryset.count() > 0)
        self.assertEqual(queryset.count(), queryset2.count())

    @patch('mspray.apps.warehouse.store.ingest_sprayday')
    @patch('mspray.apps.warehouse.store.create_sprayday_druid_json_file')
    @patch('mspray.apps.warehouse.store.get_sprayday_queryset_from_x_minutes')
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
        self.assertEqual(kwargs['intervals'], get_druid_intervals(queryset))

    @patch('mspray.apps.warehouse.store.ingest_sprayday')
    @patch('mspray.apps.warehouse.store.create_sprayday_druid_json_file')
    def test_get_historical_data_day(self, json_file_mock, ingest_mock):
        """
        Asset that the filename is correct when you supply just the day
        """
        path = "/".join([str(x) for x in [None, None, 10] if x is not None])
        filename = "{}/".format(settings.DRUID_SPRAYDAY_DATASOURCE) + path +\
            "/sprayday.json"
        get_historical_data(day=10)
        self.assertTrue(json_file_mock.called)
        self.assertTrue(ingest_mock.called)
        args, kwargs = json_file_mock.call_args_list[0]
        self.assertEqual(kwargs['filename'], filename)

    @patch('mspray.apps.warehouse.store.ingest_sprayday')
    @patch('mspray.apps.warehouse.store.create_sprayday_druid_json_file')
    def test_get_historical_data_month(self, json_file_mock, ingest_mock):
        """
        Asset that the filename is correct when you supply just the month
        """
        path = "/".join([str(x) for x in [None, 10, None] if x is not None])
        filename = "{}/".format(settings.DRUID_SPRAYDAY_DATASOURCE) + path +\
            "/sprayday.json"
        get_historical_data(month=10)
        self.assertTrue(json_file_mock.called)
        self.assertTrue(ingest_mock.called)
        args, kwargs = json_file_mock.call_args_list[0]
        self.assertEqual(kwargs['filename'], filename)

    @patch('mspray.apps.warehouse.store.ingest_sprayday')
    @patch('mspray.apps.warehouse.store.create_sprayday_druid_json_file')
    def test_get_historical_data_year(self, json_file_mock, ingest_mock):
        """
        Asset that the filename is correct when you supply just the year
        """
        path = "/".join([str(x) for x in [2017, None, None] if x is not None])
        filename = "{}/".format(settings.DRUID_SPRAYDAY_DATASOURCE) + path +\
            "/sprayday.json"
        get_historical_data(year=2017)
        self.assertTrue(json_file_mock.called)
        self.assertTrue(ingest_mock.called)
        args, kwargs = json_file_mock.call_args_list[0]
        self.assertEqual(kwargs['filename'], filename)

    @patch('mspray.apps.warehouse.store.get_druid_intervals')
    @patch('mspray.apps.warehouse.store.ingest_sprayday')
    @patch('mspray.apps.warehouse.store.create_sprayday_druid_json_file')
    def test_get_historical_data(self, json_file_mock, ingest_mock,
                                 intervals_mock):
        """
        Test that get historical data actually works by ensuring it calls
        ingest_sprayday with the right arguments
        """
        path = "/".join([str(x) for x in [2017, 10, 10] if x is not None])
        filename = "{}/".format(settings.DRUID_SPRAYDAY_DATASOURCE) + path +\
            "/sprayday.json"
        json_file_mock.return_value = filename
        intervals_mock.return_value = "2013-01-01/2013-01-02"
        get_historical_data(day=10, month=10, year=2017)
        self.assertTrue(json_file_mock.called)
        self.assertTrue(ingest_mock.called)
        mock1_args, mock1_kwargs = json_file_mock.call_args_list[0]
        self.assertEqual(mock1_kwargs['filename'], filename)
        mock2_args, mock2_kwargs = ingest_mock.call_args_list[0]
        self.assertEqual(mock2_args[0], settings.AWS_S3_BASE_URL + filename)
        self.assertEqual(mock2_kwargs['intervals'], "2013-01-01/2013-01-02")

    def test_create_sprayday_druid_json_file(self):
        """
        Test that create_sprayday_druid_json_file actually gets the right JSON
        data and that it saves it and returns the filename
        """
        queryset = SprayDay.objects.order_by('spray_date')[:10]

        try:
            os.remove("/tmp/somefile.json")
        except OSError:
            pass

        lines = []
        for record in queryset_iterator(queryset, 1000):
            data = SprayDayDruidSerializer(record).data
            line = JSONRenderer().render(data)
            lines.append(line)

        expected_content = b'\n'.join(lines)

        default_file_storage = 'django.core.files.storage.FileSystemStorage'
        with self.settings(DEFAULT_FILE_STORAGE=default_file_storage,
                           MEDIA_ROOT="/tmp/"):
            result = create_sprayday_druid_json_file(queryset=queryset,
                                                     filename="somefile.json")
            self.assertEqual(result, "/tmp/somefile.json")
            with open(result, "r") as f:
                content = f.read()
            self.assertEqual(content.encode(), expected_content)
