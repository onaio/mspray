# -*- coding: utf-8 -*-
"""
Test sensitization_visit module.
"""
from django.test import TestCase

from mspray.apps.main.models.sensitization_visit import (
    SensitizationVisit,
    create_sensitization_visit,
)
from mspray.apps.main.tests.utils import SENSITIZATION_VISIT_DATA, data_setup


class TestSensitizationVisit(TestCase):
    """Test SensitizationVisit class"""

    def test_create_sensitization_visit(self):
        """Test create_sensitization_visit() function"""
        data_setup()
        sensitization_visit = create_sensitization_visit(
            SENSITIZATION_VISIT_DATA
        )
        self.assertIsInstance(sensitization_visit, SensitizationVisit)
        self.assertTrue(sensitization_visit.is_sensitized)
        self.assertTrue(sensitization_visit.spray_area.is_sensitized)
