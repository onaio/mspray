# -*- coding: utf-8 -*-
"""
Test MDA views.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from mspray.apps.main.models import Location
from mspray.apps.main.tests.utils import data_setup
from mspray.apps.mda.views.spray_area import SprayAreaView


class TestSprayAreaView(TestCase):
    """Test SprayArea views."""

    def test_spray_area_view(self):
        """Test SprayAreaView"""
        data_setup()
        factory = RequestFactory()
        request = factory.get("/mda")
        view = SprayAreaView.as_view()
        response = view(request)
        self.assertContains(response, "All Eligible Areas", status_code=200)
        self.assertContains(response, "Lusaka", 2, status_code=200)
        self.assertContains(response, "Mtendere", 2, status_code=200)
        self.assertContains(response, "Akros_1", 1, status_code=200)
        self.assertContains(response, "Akros_2", 1, status_code=200)

        # test uri
        self.assertEqual(reverse("mda:index"), "/mda/")

        # test targeted
        akros_1 = Location.objects.get(name="Akros_1")
        akros_1.target = False
        akros_1.save()
        response = view(request)
        self.assertContains(response, "Akros_1", 0, status_code=200)

        # test CSV
        response = view(request, **{"format": "csv"})
        self.assertContains(response, "Akros_2,", 1, status_code=200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="sprayareas.csv"',
        )
