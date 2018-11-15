"""Test mobilisation module."""
from django.test import RequestFactory, TestCase

from mspray.apps.main.models import Mobilisation, SensitizationVisit
from mspray.apps.main.tests.utils import (
    MOBILISATION_VISIT_DATA, SENSITIZATION_VISIT_DATA, data_setup)
from mspray.apps.main.views.mobilisation import MobilisationView
from mspray.apps.main.views.sensitization_visit import SensitizationVisitView

from mspray.apps.main.views.home import TargetAreaView


class TestTargetAreaView(TestCase):
    """Test mobilisation view."""

    def test_mobilisation(self):
        """Test processing a mobilisation visit via MobilisationView."""
        data_setup()
        data = MOBILISATION_VISIT_DATA
        factory = RequestFactory()
        view = MobilisationView.as_view()
        request = factory.post("/mobilisation", data)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        visit = Mobilisation.objects.get(submission_id=data["_id"])
        self.assertTrue(visit.is_mobilised)

        view = TargetAreaView.as_view()
        request = factory.get("/2/3")
        response = view(
            request, district_pk=visit.health_facility_id,
            slug=visit.spray_area_id)
        self.assertContains(
            response,
            'Mobilised? \
            <i class="fa fa-check-circle" style="color: green"></i>',
            html=True)
        self.assertContains(
            response,
            'Community Ready?  <i class="fa fa-times" style="color: red"></i>',
            html=True)

    def test_sensitization(self):
        """Test processing a sensitiza visit via MobilisationView."""
        data_setup()
        data = SENSITIZATION_VISIT_DATA
        factory = RequestFactory()
        view = SensitizationVisitView.as_view()
        request = factory.post("/sensitization_visit", data)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        visit = SensitizationVisit.objects.get(submission_id=data["_id"])
        self.assertTrue(visit.is_sensitized)

        view = TargetAreaView.as_view()
        request = factory.get("/2/3")
        response = view(
            request, district_pk=visit.health_facility_id,
            slug=visit.spray_area_id)
        self.assertContains(
            response,
            'Mobilised? <i class="fa fa-times" style="color: red"></i>',
            html=True)
        self.assertContains(
            response,
            'Community Ready? \
            <i class="fa fa-check-circle" style="color: green"></i>',
            html=True)
