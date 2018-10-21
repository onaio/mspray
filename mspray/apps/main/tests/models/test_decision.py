# -*- coding: utf-8 -*-
"""
Test sensitization_visit module.
"""
from django.test import TestCase

from mspray.apps.main.models.decision import Decision, create_decision_visit
from mspray.apps.main.tests.utils import DECISION_VISIT_DATA, data_setup


class TestDecision(TestCase):
    """Test Decision class"""

    def test_create_decision_visit(self):
        """Test create_decision_visit() function"""
        data_setup()
        decision_visit = create_decision_visit(DECISION_VISIT_DATA)
        self.assertIsInstance(decision_visit, Decision)
        self.assertEqual(
            decision_visit.spray_area.last_decision_date, decision_visit.today
        )
