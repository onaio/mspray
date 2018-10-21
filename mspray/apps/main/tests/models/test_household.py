# -*- coding: utf-8 -*-
"""
Test Household model module.
"""
from django.test import TestCase

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.location import Location
from mspray.apps.main.tests.utils import data_setup, load_spray_data


class TestHousehold(TestCase):
    """Test Household model class"""

    def test_sprayable(self):
        """Test sprayable."""
        data_setup()
        load_spray_data()
        self.assertEqual(Household.objects.filter(sprayable=False).count(), 4)

        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.not_sprayable, 4)
