"""module to test reveal utils"""
from datetime import date

from django.contrib.gis.geos import Point

from mspray.apps.main.models import Household, SprayDay
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reveal.utils import add_spray_data

from django.test import override_settings

REVEAL_SPRAY_STATUS_FIELD = "spray_status"
REVEAL_NOT_SPRAYABLE_VALUE = "Not Sprayable"
REVEAL_SPRAYED_VALUE = "Sprayed"
REVEAL_DATE_FIELD = "date"


@override_settings(
    REVEAL_SPRAY_STATUS_FIELD=REVEAL_SPRAY_STATUS_FIELD,
    REVEAL_NOT_SPRAYABLE_VALUE=REVEAL_NOT_SPRAYABLE_VALUE,
    REVEAL_SPRAYED_VALUE=REVEAL_SPRAYED_VALUE,
    REVEAL_DATE_FIELD=REVEAL_DATE_FIELD,
    REVEAL_GPS_FIELD="location",
    MSPRAY_OSM_PRESENCE_FIELD=False,
    SPRAYABLE_FIELD=REVEAL_SPRAY_STATUS_FIELD,
    MSPRAY_WAS_SPRAYED_FIELD=REVEAL_SPRAY_STATUS_FIELD,
    NOT_SPRAYABLE_VALUE=REVEAL_NOT_SPRAYABLE_VALUE,
    SPRAYED_VALUE=REVEAL_SPRAYED_VALUE,
    SPRAYED_VALUES=[REVEAL_SPRAYED_VALUE],
    MSPRAY_DATE_FIELD=REVEAL_DATE_FIELD,
    CELERY_TASK_ALWAYS_EAGER=True,
)
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
        Test add_spray_data for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": 1337,
            "date": "2015-09-21",
            "location": "-15.41818400162254, 28.35517894260948",
            "spray_status": "Sprayed"
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

        sprayday = SprayDay.objects.first()
        self.assertEqual(1337, sprayday.submission_id)
        self.assertEqual(date(2015, 9, 21), sprayday.spray_date)
        self.assertEqual(
            Point(float(28.35517894260948), float(-15.41818400162254)).coords,
            sprayday.geom.coords)
        self.assertTrue(sprayday.location is not None)
        self.assertEqual(
            sprayday.location,
            Household.objects.filter(
                geom__contains=sprayday.geom).first().location)
        self.assertTrue(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.household.visited)
        self.assertTrue(sprayday.household.sprayable)

    def test_add_spray_data_not_sprayed(self):
        """
        Test add_spray_data NOT SPRAYED for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": 1337,
            "date": "2015-09-21",
            "location": "-15.41818400162254, 28.35517894260948",
            "spray_status": "Not Sprayed - Refused"
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertFalse(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.household.visited)
        self.assertTrue(sprayday.household.sprayable)

    def test_add_spray_data_not_visited(self):
        """
        Test add_spray_data NOT VISITED for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": 1337,
            "date": "2015-09-21",
            "location": "-15.41818400162254, 28.35517894260948",
            "spray_status": "Not Visited"
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertFalse(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertFalse(sprayday.household.visited)
        self.assertTrue(sprayday.household.sprayable)

    def test_add_spray_data_not_sprayable(self):
        """
        Test add_spray_data NOT SPRAYABLE for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": 1337,
            "date": "2015-09-21",
            "location": "-15.41818400162254, 28.35517894260948",
            "spray_status": "Not Sprayable"
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertFalse(sprayday.was_sprayed)
        self.assertFalse(sprayday.sprayable)
        self.assertTrue(sprayday.household.visited)
        self.assertFalse(sprayday.household.sprayable)
