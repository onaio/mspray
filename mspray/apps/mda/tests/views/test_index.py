# -*- coding: utf-8 -*-
"""
Test MDA views.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.http import Http404

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

        # test uri
        self.assertEqual(reverse("mda:index"), "/mda/")

        # test targeted
        lusaka = Location.objects.get(name="Lusaka")
        lusaka.target = False
        lusaka.save()
        response = view(request)
        self.assertContains(response, "Lusaka", 0, status_code=200)

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

        # test uri
        self.assertEqual(
            reverse("mda:location", kwargs={"location": location.pk}),
            "/mda/{}".format(location.pk),
        )

        # test targeted
        health_facility = Location.objects.filter(level="RHC").first()
        health_facility.target = False
        health_facility.save()
        response = view(request, location=location.pk)
        self.assertContains(response, health_facility.name, 0, 200)

        # check catchment view - 404 when not targeted
        with self.assertRaises(Http404):
            response = view(request, location=health_facility.pk)
