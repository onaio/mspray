# -*- coding: utf-8 -*-
"""
Test decision module.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from mspray.apps.main.models import Decision
from mspray.apps.main.tests.utils import DECISION_VISIT_DATA, data_setup
from mspray.apps.main.views.decision import DecisionView


class TestDecision(TestCase):
    """Test decision view."""

    def test_create_decision(self):
        """Test processing a decision visit via DecisionView.
        """
        data_setup()
        data = DECISION_VISIT_DATA
        factory = RequestFactory()
        view = DecisionView.as_view()
        request = factory.post("/decision", data)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        visit = Decision.objects.get(submission_id=data["_id"])
        self.assertTrue(visit.today is not None)

    def test_decision_url(self):
        """Test decision-visit URL"""
        self.assertEqual(reverse("decision-visit"), "/decision-visit")
