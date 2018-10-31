# -*- coding: utf-8 -*-
"""
Test Location model module.
"""
import datetime

from django.test import TestCase

from mspray.apps.main.models.decision import Decision, create_decision_visit
from mspray.apps.main.models.location import Location
from mspray.apps.main.tests.utils import (
    DECISION_VISIT_DATA,
    data_setup,
    load_spray_data,
)


class TestLocation(TestCase):
    """Test Location model class"""

    def test_number_of_hfc_to_mopup(self):
        """Test calculating number of health facilities that need mopup."""
        data_setup()
        lusaka = Location.objects.get(name="Lusaka", level="district")
        self.assertEqual(lusaka.health_centers_to_mopup, 1)

    def test_spray_areas_to_mopup(self):
        """Test calculating number of spray_areas that need mopup."""
        data_setup()
        lusaka = Location.objects.get(name="Lusaka", level="district")
        self.assertEqual(lusaka.spray_areas_to_mopup, 2)

    def test_structures_to_mopup(self):
        """Test calculating number of structures that need mopup."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.structures_to_mopup, 12)

        load_spray_data()
        akros_2.refresh_from_db()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        # 90th percentile is 8 , sprayed is 5, difference is 3
        self.assertEqual(akros_2.structures_to_mopup, 3)

        lusaka = Location.objects.get(name="Lusaka", level="district")
        self.assertEqual(lusaka.structures_to_mopup, 15)

    def test_visited_sprayed(self):
        """Test return number of structures visited that were sprayed."""
        data_setup()
        load_spray_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.visited_sprayed, 5)

    def test_mopup_days_needed(self):
        """Test return number of mopup days needed."""
        data_setup()
        with self.settings(MOPUP_DAYS_DENOMINATOR=5):
            akros_2 = Location.objects.get(name="Akros_2", level="ta")
            self.assertEqual(akros_2.mopup_days_needed, 3)

            lusaka = Location.objects.get(name="Lusaka", level="district")
            self.assertEqual(lusaka.mopup_days_needed, 6)

            # load some spray data
            load_spray_data()

            akros_2 = Location.objects.get(name="Akros_2", level="ta")
            self.assertEqual(akros_2.mopup_days_needed, 0)

            lusaka = Location.objects.get(name="Lusaka", level="district")
            self.assertEqual(lusaka.mopup_days_needed, 3)

    def test_structures_on_ground(self):
        """Test structures_on_ground"""
        data_setup()
        load_spray_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.structures_on_ground, 9)

    def test_visited_found(self):
        """Test found"""
        data_setup()
        load_spray_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.visited_found, 8)

    def test_last_visit(self):
        """Test last_visit"""
        data_setup()
        load_spray_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.last_visit, datetime.date(2018, 9, 20))

    def test_last_decision_date(self):
        """Test last_decision_date"""
        data_setup()
        load_spray_data()
        decision_visit = create_decision_visit(DECISION_VISIT_DATA)
        self.assertIsInstance(decision_visit, Decision)
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.last_visit, datetime.date(2018, 9, 20))
        self.assertEqual(akros_2.last_decision_date, "2018-09-25")
