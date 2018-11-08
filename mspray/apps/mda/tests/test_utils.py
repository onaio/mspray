# -*- coding: utf-8 -*-
"""
Test MDA functionality in mspray.apps.main.utils module.
"""

from django.test import TestCase, override_settings

from mspray.apps.main.models import SprayDay
from mspray.apps.main.tests.utils import data_setup
from mspray.apps.main.utils import add_spray_data
from mspray.apps.mda.tests.utils import get_mda_data


@override_settings(
    SPRAYABLE_FIELD="values_from_omk/mda_status",
    MSPRAY_WAS_SPRAYED_FIELD="values_from_omk/mda_status",
    SPRAYED_VALUES=["all_received", "some_received"],
)
class TestUtils(TestCase):
    """Test MDA functionality in mspray.apps.main.utils"""

    def test_add_mda_data(self):
        """Test processing MDA status submissions."""
        data_setup()
        data = get_mda_data()
        self.assertTrue(len(data) > 4)

        # noteligible
        self.assertEqual(SprayDay.objects.count(), 0)
        sprayday = add_spray_data(data[0])
        self.assertEqual(SprayDay.objects.count(), 1)
        self.assertIsInstance(sprayday, SprayDay)
        self.assertIsNotNone(sprayday.household)
        self.assertIsNotNone(sprayday.location)
        self.assertEqual(sprayday.location.name, "Akros_2")
        self.assertFalse(sprayday.sprayable)
        self.assertFalse(sprayday.was_sprayed)
        self.assertEqual(
            sprayday.data["values_from_omk/mda_status"], "noteligible"
        )

        sprayday = add_spray_data(data[1])
        self.assertEqual(SprayDay.objects.count(), 2)
        self.assertIsInstance(sprayday, SprayDay)
        self.assertIsNotNone(sprayday.household)
        self.assertTrue(sprayday.household.sprayable)
        self.assertIsNotNone(sprayday.location)
        self.assertEqual(sprayday.location.name, "Akros_2")
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.was_sprayed)
        self.assertEqual(
            sprayday.data["values_from_omk/mda_status"], "all_received"
        )

        sprayday = add_spray_data(data[2])
        self.assertEqual(SprayDay.objects.count(), 3)
        self.assertIsInstance(sprayday, SprayDay)
        self.assertIsNotNone(sprayday.household)
        self.assertIsNotNone(sprayday.location)
        self.assertEqual(sprayday.location.name, "Akros_2")
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.was_sprayed)
        self.assertEqual(
            sprayday.data["values_from_omk/mda_status"], "some_received"
        )

        sprayday = add_spray_data(data[3])
        self.assertEqual(SprayDay.objects.count(), 4)
        self.assertIsInstance(sprayday, SprayDay)
        self.assertIsNotNone(sprayday.household)
        self.assertIsNotNone(sprayday.location)
        self.assertEqual(sprayday.location.name, "Akros_2")
        self.assertTrue(sprayday.sprayable)
        self.assertFalse(sprayday.was_sprayed)
        self.assertEqual(
            sprayday.data["values_from_omk/mda_status"], "none_received"
        )

        sprayday = add_spray_data(data[5])
        self.assertEqual(SprayDay.objects.count(), 5)
        self.assertIsInstance(sprayday, SprayDay)
        self.assertIsNone(sprayday.household)
        self.assertIsNotNone(sprayday.location)
        self.assertEqual(sprayday.location.name, "Akros_2")
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.was_sprayed)
        self.assertEqual(
            sprayday.data["values_from_omk/mda_status"], "some_received"
        )
