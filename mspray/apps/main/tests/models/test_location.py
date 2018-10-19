# -*- coding: utf-8 -*-
"""
Test Location model module.
"""
from django.test import TestCase

from mspray.apps.main.models.location import Location
from mspray.apps.main.tests.utils import data_setup, load_spray_data


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
        load_spray_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.structures_to_mopup, 1)

        lusaka = Location.objects.get(name="Lusaka", level="district")
        self.assertEqual(lusaka.structures_to_mopup, 2)

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

            akros_2.refresh_from_db()
            self.assertEqual(akros_2.mopup_days_needed, 0)

            self.assertEqual(lusaka.mopup_days_needed, 3)
