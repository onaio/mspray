# -*- coding: utf-8 -*-
"""
Test sensitization_visit module.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from mspray.apps.main.models import SensitizationVisit
from mspray.apps.main.tests.utils import SENSITIZATION_VISIT_DATA, data_setup
from mspray.apps.main.views.sensitization_visit import index


class TestSensitizationVisit(TestCase):
    """Test sensitization_visit view."""

    def test_index(self):
        """Test index view - processing a sensitization_visit"""
        data_setup()
        data = SENSITIZATION_VISIT_DATA
        factory = RequestFactory()
        request = factory.post("/sensitization_visit", data)
        response = index(request)
        self.assertEqual(response.status_code, 201)
        visit = SensitizationVisit.objects.get(submission_id=data["_id"])
        self.assertTrue(visit.is_sensitized)

    def test_index_url(self):
        """Test sensitization-visit URL"""
        self.assertEqual(reverse(index), "/sensitization-visit")
