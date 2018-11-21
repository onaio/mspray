"""module to test reveal utils"""
from datetime import date

from django.contrib.gis.geos import Point

from mspray.apps.main.models import Household, SprayDay
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reveal.utils import add_spray_data


class TestUtils(TestBase):
    """
    Utils test class
    """

    def setUp(self):
        """
        setup test class
        """
        super().setUp()
        self._load_fixtures()

    def test_add_spray_data(self):
        """
        Test add_spray_data
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": 1337,
            "date": "2015-09-21",
            "location": "-15.4183222196675, 28.35119431662"
        }
        add_spray_data(data=input_data)
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
