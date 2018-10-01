# -*- coding: utf-8 -*-
"""
Test sensitization_visit module.
"""
from django.test import TestCase

from mspray.apps.main.models.mobilisation import (
    Mobilisation,
    create_mobilisation_visit,
)
from mspray.apps.main.tests.utils import MOBILISATION_VISIT_DATA, data_setup


class TestMobilisation(TestCase):
    """Test Mobilisation class"""

    def test_create_mobilisation_visit(self):
        """Test create_mobilisation_visit() function"""
        data_setup()
        mobilisation_visit = create_mobilisation_visit(MOBILISATION_VISIT_DATA)
        self.assertIsInstance(mobilisation_visit, Mobilisation)
        self.assertTrue(mobilisation_visit.is_mobilised)
        self.assertTrue(mobilisation_visit.spray_area.is_mobilised)
