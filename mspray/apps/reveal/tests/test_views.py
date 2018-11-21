"""reveal vies moduke"""
import json
from datetime import date

from django.contrib.gis.geos import Point
from django.test import override_settings
from rest_framework.test import APIRequestFactory

from mspray.apps.main.models import Household, SprayDay
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reveal.views import add_spray_data_view


@override_settings(ROOT_URLCONF='mspray.apps.reveal.urls')
class TestViewss(TestBase):
    """
    Viewss test class
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
        payload = {
            "id": 1337,
            "date": "2015-09-21",
            "location": "-15.4183222196675, 28.35119431662"
        }
        request = self.factory.post(
            'add-spray-data',
            data=json.dumps(payload),
            content_type='application/json')
        res = add_spray_data_view(request)

        # we got the right response
        self.assertEqual(200, res.status_code)
        self.assertEqual({"success": True}, res.data)

        # we added the sprayday object
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertEqual(1337, sprayday.submission_id)
        self.assertEqual(date(2015, 9, 21), sprayday.spray_date)
        self.assertEqual(
            Point(float(28.35119431662), float(-15.4183222196675)).coords,
            sprayday.geom.coords)
        self.assertTrue(sprayday.location is not None)
        self.assertEqual(
            sprayday.location,
            Household.objects.filter(
                geom__contains=sprayday.geom).first().location)
