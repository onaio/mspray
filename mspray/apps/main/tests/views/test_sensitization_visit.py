# -*- coding: utf-8 -*-
"""
Test sensitization_visit module.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from mspray.apps.main.models import SensitizationVisit
from mspray.apps.main.tests.utils import SENSITIZATION_VISIT_DATA, data_setup
from mspray.apps.main.views.sensitization_visit import (
    SensitizationVisitViewSet
)


class TestSensitizationVisit(TestCase):
    """Test sensitization_visit view."""

    def test_create_sensitization_visit(self):
        """Test processing a sensitization visit via SensitizationVisitViewSet.
        """
        data_setup()
        data = SENSITIZATION_VISIT_DATA
        factory = RequestFactory()
        view = SensitizationVisitViewSet.as_view({"post": "create"})
        request = factory.post("/sensitization_visit", data)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        visit = SensitizationVisit.objects.get(submission_id=data["_id"])
        self.assertTrue(visit.is_sensitized)

    def test_sensitization_visit_url(self):
        """Test sensitization-visit URL"""
        self.assertEqual(
            reverse("sensitization-visit"), "/sensitization-visit"
        )
