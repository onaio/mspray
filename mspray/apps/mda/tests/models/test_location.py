# -*- coding: utf-8 -*-
"""
Test Location model module.
"""

from django.test import TestCase, override_settings

from mspray.apps.main.models.location import Location
from mspray.apps.main.tests.utils import data_setup
from mspray.apps.mda.tests.utils import load_mda_data


@override_settings(
    SPRAYABLE_FIELD="values_from_omk/mda_status",
    MSPRAY_WAS_SPRAYED_FIELD="values_from_omk/mda_status",
    SPRAYED_VALUES=["all_received", "some_received"],
)
class TestLocation(TestCase):
    """Test Location model class"""

    def test_mda_structures(self):
        """Test mda_structures."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.mda_structures, 13)

    def test_mda_found(self):
        """Test mda_found."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.mda_found, 0)

        load_mda_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.mda_found, 4)

    def test_mda_received(self):
        """Test mda_received."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.mda_received, 0)

        load_mda_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.mda_received, 3)

    def test_population_eligible(self):
        """Test mda_received."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.population_eligible, 0)

        load_mda_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.population_eligible, 1)
