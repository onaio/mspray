# -*- coding: utf-8 -*-
"""
Test Household model module.
"""
from django.test import TestCase

from mspray.apps.main.models.household import Household
from mspray.apps.main.tests.utils import data_setup, load_spray_data


class TestHousehold(TestCase):
    """Test Household model class"""

    def test_sprayable(self):
        """Test sprayable."""
        data_setup()
        load_spray_data()
        self.assertEqual(Household.objects.filter(sprayable=False).count(), 4)
