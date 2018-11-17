# -*- coding: utf-8 -*-
"""
Test MDA views.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from mspray.apps.main.models import Location
from mspray.apps.main.tests.utils import data_setup
from mspray.apps.mda.views.index import MDALocationView, MDAView


class TestMDAView(TestCase):
    """Test MDA views."""

    def test_mda_view(self):
        """Test MDAView"""
        data_setup()
        factory = RequestFactory()
        request = factory.get("/mda")
        view = MDAView.as_view()
        response = view(request)
        self.assertContains(response, "MDA", status_code=200)
        self.assertContains(response, "Lusaka", 1, status_code=200)

        self.assertEqual(reverse("mda:index"), "/mda/")

    def test_mda_location_view(self):
        """Test MDALocationView"""
        data_setup()
        location = Location.objects.filter(level="district").first()
        factory = RequestFactory()
        request = factory.get("/mda/{}".format(location.pk))
        view = MDALocationView.as_view()
        response = view(request, location=location.pk)
        self.assertContains(response, "MDA", status_code=200)
        self.assertContains(response, "Mtendere", 1, status_code=200)
        self.assertContains(response, "Lusaka", 1, status_code=200)

        self.assertEqual(
            reverse("mda:location", kwargs={"location": location.pk}),
            "/mda/{}".format(location.pk),
        )
