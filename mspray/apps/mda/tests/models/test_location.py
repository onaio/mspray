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

    def test_structures_on_ground(self):
        """Test structures_on_ground."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.structures_on_ground, 13)

    def test_mda_found(self):
        """Test mda_found."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.mda_found, 0)

        load_mda_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.mda_found, 4)

    def test_mda_visited_sprayed(self):
        """Test MDA location.visited_sprayed."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.visited_sprayed, 0)

        load_mda_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.visited_sprayed, 3)

    def test_population_eligible(self):
        """Test population_eligible."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.population_eligible, 0)

        load_mda_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.population_eligible, 1)

    def test_population_treatment(self):
        """Test population_treatment."""
        data_setup()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.population_treatment, 0)

        load_mda_data()
        akros_2 = Location.objects.get(name="Akros_2", level="ta")
        self.assertEqual(akros_2.population_treatment, 1)

    def test_mda_spray_areas_found(self):
        """Test a spray is is found if only 20% has been sprayed"""
        data_setup()
        hfc = Location.objects.get(name="Mtendere")
        self.assertEqual(hfc.mda_spray_areas_found, 0)
        self.assertEqual(
            [
                foci.mda_received_percentage
                for foci in hfc.location_set.all().order_by("name")
            ],
            [0.0, 0.0],
        )

        load_mda_data()
        hfc = Location.objects.get(name="Mtendere")
        self.assertEqual(hfc.mda_spray_areas_found, 1)
        self.assertEqual(
            [
                foci.mda_received_percentage
                for foci in hfc.location_set.all().order_by("name")
            ],
            [0.0, 25.0],
        )

    def test_mda_spray_areas_received(self):
        """Test a spray is is received if only 90% has been sprayed"""
        data_setup()
        hfc = Location.objects.get(name="Mtendere")
        self.assertEqual(hfc.mda_spray_areas_received, 0)
        self.assertEqual(
            [
                foci.mda_received_percentage
                for foci in hfc.location_set.all().order_by("name")
            ],
            [0.0, 0.0],
        )

        load_mda_data()
        hfc = Location.objects.get(name="Mtendere")
        self.assertEqual(hfc.mda_spray_areas_received, 0)
        self.assertEqual(
            [
                foci.mda_received_percentage
                for foci in hfc.location_set.all().order_by("name")
            ],
            [0.0, 25.0],
        )
