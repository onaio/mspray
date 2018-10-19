# -*- coding: utf-8 -*-
"""
Test mobilisation module.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from mspray.apps.main.models import Mobilisation
from mspray.apps.main.tests.utils import MOBILISATION_VISIT_DATA, data_setup
from mspray.apps.main.views.mobilisation import MobilisationView


class TestMobilisation(TestCase):
    """Test mobilisation view."""

    def test_create_mobilisation(self):
        """Test processing a mobilisation visit via MobilisationView.
        """
        data_setup()
        data = MOBILISATION_VISIT_DATA
        factory = RequestFactory()
        view = MobilisationView.as_view()
        request = factory.post("/mobilisation", data)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        visit = Mobilisation.objects.get(submission_id=data["_id"])
        self.assertTrue(visit.is_mobilised)

    def test_mobilisation_url(self):
        """Test mobilisation-visit URL"""
        self.assertEqual(reverse("mobilisation-visit"), "/mobilisation-visit")
