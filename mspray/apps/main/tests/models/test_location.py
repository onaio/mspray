# -*- coding: utf-8 -*-
"""
Test Location model module.
"""
from django.test import TestCase

from mspray.apps.main.models.location import Location
from mspray.apps.main.tests.utils import data_setup


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
        lusaka = Location.objects.get(name="Lusaka", level="district")
        self.assertEqual(lusaka.structures_to_mopup, 2)
