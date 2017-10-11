from unittest.mock import patch
from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay, Location, TeamLeader
from mspray.apps.alerts.tasks import user_distance, health_facility_catchment
from mspray.apps.alerts.tasks import health_facility_catchment_hook
from mspray.apps.alerts.tasks import so_daily_form_completion
from mspray.celery import app


class TestTasks(TestBase):

    hf_druid_result = [
        {'event': {'num_not_sprayed': 1, 'target_area_name': 'Lusaka_6000',
                   'rhc_name': 'Akros', 'num_not_sprayable': 2,
                   'num_refused': 1, 'target_area_id': '1463',
                   'num_found': 3.0, 'num_sprayed_duplicates': 0,
                   'rhc_id': '1462', 'num_sprayed_no_duplicates': 2,
                   'num_new_no_duplicates': 1,
                   'num_not_sprayed_no_duplicates': 1,
                   'target_area_structures': '37', 'num_duplicate': 0,
                   'district_id': '1460', 'num_new': 1, 'district_name':
                   'Lusaka', 'num_not_sprayable_no_duplicates': 2,
                   'num_sprayed': 2},
         'timestamp': '1917-09-08T00:00:00.000Z',
         'version': 'v1'},
        {'event': {'num_not_sprayed': 3, 'target_area_name': 'Lusaka_7000',
                   'rhc_name': 'Akros', 'num_not_sprayable': 1,
                   'num_refused': 3, 'target_area_id': '1464',
                   'num_found': 11.0, 'num_sprayed_duplicates': 0,
                   'rhc_id': '1462', 'num_sprayed_no_duplicates': 8,
                   'num_new_no_duplicates': 1,
                   'num_not_sprayed_no_duplicates': 3,
                   'target_area_structures': '41', 'num_duplicate': 0,
                   'district_id': '1460', 'num_new': 1,
                   'district_name': 'Lusaka',
                   'num_not_sprayable_no_duplicates': 1, 'num_sprayed': 8},
         'timestamp': '1917-09-08T00:00:00.000Z',
         'version': 'v1'}]

    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self._load_fixtures()

    @patch('mspray.apps.alerts.tasks.start_flow')
    def test_user_distance(self, mock):
        sprayday = SprayDay.objects.first()
        user_distance(sprayday.id)
        self.assertTrue(mock.called)

    @patch('mspray.apps.alerts.tasks.get_druid_data',
           return_value=hf_druid_result)
    @patch('mspray.apps.alerts.tasks.start_flow')
    def test_health_facility_catchment(self, mock, mock2):
        record = SprayDay.objects.filter(location__parent__id=1461).first()
        health_facility_catchment(record.id, force=True)
        self.assertTrue(mock.called)
        self.assertTrue(mock2.called)

    @patch('mspray.apps.alerts.tasks.health_facility_catchment')
    def test_health_facility_catchment_hook(self, mock):
        # make at least one SprayDay created on to be within last 10 hrs
        record = SprayDay.objects.last()
        ten_hours_ago = timezone.now() - timedelta(hours=10)
        record.created_on = ten_hours_ago
        record.save()
        health_facility_catchment_hook()
        self.assertTrue(mock.delay.called)

    @patch('mspray.apps.alerts.tasks.start_flow')
    def test_so_daily_form_completion(self, mock):
        district = Location.objects.filter(level='district').first()
        tla = TeamLeader.objects.first()
        so_daily_form_completion(district.code, tla.code, "Yes")
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0],
                         settings.RAPIDPRO_SO_DAILY_COMPLETION_FLOW_ID)
        self.assertEqual(args[1]['district_name'], district.name)
        self.assertEqual(args[1]['so_name'], tla.name)
        self.assertEqual(args[1]['confrimdecisionform'], "Yes")
