# -*- coding: utf-8 -*-
"""
Test sensitization_visit module.
"""
from django.test import TestCase

from mspray.apps.main.models.mobilisation import (
    Mobilisation,
    create_mobilisation_visit,
)
from django.conf import settings
from mspray.apps.main.tests.utils import MOBILISATION_VISIT_DATA, data_setup


class TestMobilisation(TestCase):
    """Test Mobilisation class."""

    def test_create_mobilisation_visit(self):
        """Test create_mobilisation_visit() function."""
        data_setup()
        mobilisation_visit = create_mobilisation_visit(MOBILISATION_VISIT_DATA)
        self.assertIsInstance(mobilisation_visit, Mobilisation)
        self.assertTrue(mobilisation_visit.is_mobilised)
        self.assertTrue(mobilisation_visit.spray_area.is_mobilised)

    def test_link_mobilisation_visit_via_spatial_query(self):
        """Test create_mobilisation_visit() function."""
        data_setup()
        gps_data = MOBILISATION_VISIT_DATA
        gps_data["osmstructure:way:id"] = 525683350
        gps_data['osmstructure:ctr:lat'] = -15.418780034209806
        gps_data['osmstructure:ctr:lon'] = 28.35196267147328

        mobilisation = create_mobilisation_visit(gps_data)
        self.assertIsNotNone(mobilisation.spray_area)
        self.assertIsInstance(mobilisation, Mobilisation)
        self.assertEqual(gps_data['spray_area'], '01_1')
        self.assertEqual(mobilisation.spray_area.name, 'Akros_1')
