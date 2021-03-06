"""reveal vies module"""
from datetime import date

from django.contrib.gis.geos import Point
from django.test import override_settings

from rest_framework.test import APIRequestFactory

from mspray.apps.main.models import Household, SprayDay
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reveal.views import add_spray_data_view


@override_settings(ROOT_URLCONF="mspray.apps.reveal.urls")
class TestViews(TestBase):
    """
    Views test class
    """

    def setUp(self):
        """
        setup test class
        """
        super().setUp()
        self.factory = APIRequestFactory()
        self._load_fixtures()

    def test_add_spray_data_view(self):
        """
        Test add_spray_data_view
        """
        SprayDay.objects.all().delete()
        payload = """{
            "id": "156729",
            "parent_id": "3537",
            "status": "Active",
            "geometry": "{\\"type\\":\\"Point\\",\\"coordinates\\":[28.35517894260948,-15.41818400162254]}",
            "server_version": 1542970626309,
            "task_id": "2caa810d-d4da-4e67-838b-badb9bd86e06",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Sprayed",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "2015-09-21T1100",
            "task_server_version": 1543867945196
        }"""  # noqa
        request = self.factory.post(
            "add-spray-data", data=payload, content_type="application/json"
        )
        res = add_spray_data_view(request)

        # we got the right response
        self.assertEqual(200, res.status_code)
        self.assertEqual({"success": True}, res.data)

        # we added the sprayday object
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertEqual(1, sprayday.submission_id)
        self.assertEqual(date(2015, 9, 21), sprayday.spray_date)
        self.assertEqual(
            Point(float(28.35517894260948), float(-15.41818400162254)).coords,
            sprayday.geom.coords,
        )
        self.assertTrue(sprayday.location is not None)
        self.assertEqual(
            sprayday.location,
            Household.objects.filter(
                geom__contains=sprayday.geom).first().location,
        )

    def test_add_spray_data_view_polygon(self):
        """
        Test add_spray_data_view wiht polygons
        """
        SprayDay.objects.all().delete()
        payload = """{
            "id": "154147",
            "parent_id": "3951",
            "status": "Active",
            "geometry": "{\\"type\\":\\"Polygon\\",\\"coordinates\\":[[[28.3552415, -15.418094], [28.3552963, -15.4182251], [28.3552069, -15.4182598], [28.3551895, -15.4182184], [28.3550886, -15.4182576], [28.3550511, -15.418168], [28.3552415, -15.418094]]]}",
            "server_version": 1545204913897,
            "task_id": "d6058db2-0364-11e9-8eb2-f2801f1b9fd1",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Sprayed",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "",
            "task_server_version": 1545206825909
        }"""  # noqa
        request = self.factory.post(
            "add-spray-data", data=payload, content_type="application/json"
        )
        res = add_spray_data_view(request)

        # we got the right response
        self.assertEqual(200, res.status_code)
        self.assertEqual({"success": True}, res.data)

        # we added the sprayday object
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertEqual(1, sprayday.submission_id)
        self.assertEqual(date(2015, 9, 21), sprayday.spray_date)
        self.assertEqual(
            Point(float(28.35517894260948), float(-15.41818400162254)).coords,
            sprayday.geom.coords,
        )
        self.assertTrue(sprayday.location is not None)
        self.assertEqual(
            sprayday.location,
            Household.objects.filter(
                geom__contains=sprayday.geom).first().location,
        )
