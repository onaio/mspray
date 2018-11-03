from unittest.mock import patch
from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay, Location, TeamLeader
from mspray.apps.alerts.tasks import user_distance, health_facility_catchment
from mspray.apps.alerts.tasks import health_facility_catchment_hook
from mspray.apps.alerts.tasks import so_daily_form_completion, no_gps
from mspray.apps.alerts.tasks import (
    task_send_weekly_update_email,
    daily_spray_effectiveness_task,
)
from mspray.apps.alerts.serializers import UserDistanceSerializer
from mspray.apps.alerts.serializers import GPSSerializer
from mspray.celery import app


class TestTasks(TestBase):

    hf_druid_result = [
        {
            "event": {
                "num_not_sprayed": 1,
                "target_area_name": "Lusaka_6000",
                "rhc_name": "Akros",
                "num_not_sprayable": 2,
                "num_refused": 1,
                "target_area_id": "1463",
                "num_found": 3.0,
                "num_sprayed_duplicates": 0,
                "rhc_id": "1462",
                "num_sprayed_no_duplicates": 2,
                "num_new_no_duplicates": 1,
                "num_not_sprayed_no_duplicates": 1,
                "target_area_structures": "37",
                "num_duplicate": 0,
                "district_id": "1460",
                "num_new": 1,
                "district_name": "Lusaka",
                "num_not_sprayable_no_duplicates": 2,
                "num_sprayed": 2,
            },
            "timestamp": "1917-09-08T00:00:00.000Z",
            "version": "v1",
        },
        {
            "event": {
                "num_not_sprayed": 3,
                "target_area_name": "Lusaka_7000",
                "rhc_name": "Akros",
                "num_not_sprayable": 1,
                "num_refused": 3,
                "target_area_id": "1464",
                "num_found": 11.0,
                "num_sprayed_duplicates": 0,
                "rhc_id": "1462",
                "num_sprayed_no_duplicates": 8,
                "num_new_no_duplicates": 1,
                "num_not_sprayed_no_duplicates": 3,
                "target_area_structures": "41",
                "num_duplicate": 0,
                "district_id": "1460",
                "num_new": 1,
                "district_name": "Lusaka",
                "num_not_sprayable_no_duplicates": 1,
                "num_sprayed": 8,
            },
            "timestamp": "1917-09-08T00:00:00.000Z",
            "version": "v1",
        },
    ]

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self._load_fixtures()

    @patch("mspray.apps.alerts.tasks.start_flow")
    def test_user_distance(self, mock):
        """
        Test that the user distance task works:
            - assert it calls the start_flow function with the right args
        """
        sprayday = SprayDay.objects.first()
        user_data = UserDistanceSerializer(sprayday).data
        user_distance(sprayday.id)
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0], settings.RAPIDPRO_USER_DISTANCE_FLOW_ID)
        self.assertEqual(args[1], user_data)

    @patch("mspray.apps.alerts.tasks.start_flow")
    def test_no_gps(self, mock):
        """
        Test that the no_gps task works:
            - assert it calls the start_flow function with the right args
        """
        sprayday = SprayDay.objects.first()
        gps_data = GPSSerializer(sprayday).data
        no_gps(sprayday.id)
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0], settings.RAPIDPRO_NO_GPS_FLOW_ID)
        self.assertEqual(args[1], gps_data)

    @patch(
        "mspray.apps.alerts.tasks.get_druid_data", return_value=hf_druid_result
    )
    @patch("mspray.apps.alerts.tasks.start_flow")
    def test_health_facility_catchment(self, mock, mock2):
        """
        test that the health_facility_catchment task works:
            - assert that it calls the get_druid_data
            - assert that it calls start_flow with the right args
        """
        record = SprayDay.objects.filter(location__parent__id=1461).first()
        expected_druid_result = {
            "target_area_count": 1,
            "rhc_id": 1462,
            "visited_percentage": 100,
            "sprayed_percentage": 0,
            "district_id": 1460,
            "rhc_name": "Akros",
            "sprayed": 0,
            "district_name": "Lusaka",
            "sprayed_coverage": 0,
            "visited": 1,
        }
        health_facility_catchment(record.id, force=True)
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0], settings.RAPIDPRO_HF_CATCHMENT_FLOW_ID)
        self.assertEqual(args[1], expected_druid_result)
        self.assertTrue(mock2.called)

    @patch("mspray.apps.alerts.tasks.health_facility_catchment")
    def test_health_facility_catchment_hook(self, mock):
        """
        test that the health_facility_catchment_hook task works:
            - assert that it calls health_facility_catchment
        """
        # make at least one SprayDay created on to be within last 10 hrs
        record = SprayDay.objects.last()
        ten_hours_ago = timezone.now() - timedelta(hours=10)
        record.created_on = ten_hours_ago
        record.save()
        health_facility_catchment_hook()
        self.assertTrue(mock.delay.called)
        args, kwargs = mock.delay.call_args_list[0]
        self.assertEqual(args[0], record.pk)

    @patch("mspray.apps.alerts.tasks.send_weekly_update_email")
    def test_task_send_weekly_update_email(self, mock):
        """
        Test that task_send_weekly_update_email  task works and that it calls
        send_weekly_update_email
        """
        task_send_weekly_update_email()
        self.assertTrue(mock.called)

    @patch("mspray.apps.alerts.tasks.start_flow")
    def test_so_daily_form_completion(self, mock):
        """
        Test that the so_daily_form_completion task works:
            - assert it calls the start_flow function with the right args
        """
        district = Location.objects.filter(level="district").first()
        tla = TeamLeader.objects.first()
        so_daily_form_completion(district.code, tla.code, "Yes")
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(
            args[0], settings.RAPIDPRO_SO_DAILY_COMPLETION_FLOW_ID
        )
        self.assertEqual(args[1]["district_name"], district.name)
        self.assertEqual(args[1]["so_name"], tla.name)
        self.assertEqual(args[1]["confrimdecisionform"], "Yes")

    @patch("mspray.apps.alerts.tasks.daily_spray_effectiveness")
    def test_daily_spray_effectiveness(self, mocked_function):
        """Test task that triggers daily spray effectiveness notifications."""
        daily_spray_effectiveness_task.delay("flow_uuid", "2018-11-03")
        self.assertTrue(mocked_function.called)
