# -*- coding: utf-8 -*-
"""
Test load_locations_priority CSV file and set locations priority.
"""
import os

from django.core.management import call_command
from django.test import TestCase

from mspray.apps.main.models import Location
from mspray.apps.main.tests.utils import FIXTURES_DIR, data_setup


class TestLoadLocationsPriority(TestCase):
    """Test load_locations_priority command class."""

    def test_command(self):
        """Test load_locations_priority sets priority in the location."""
        data_setup()
        location = Location.objects.get(name="Akros_1")
        self.assertIsNone(location.priority)
        location = Location.objects.get(name="Akros_2")
        self.assertIsNone(location.priority)

        path = os.path.join(FIXTURES_DIR, "Lusaka", "priority.csv")
        call_command("load_locations_priority", path)
        location = Location.objects.get(name="Akros_1")
        self.assertEqual(location.priority, 1)
        location = Location.objects.get(name="Akros_2")
        self.assertEqual(location.priority, 2)
