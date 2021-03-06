# -*- coding: utf-8 -*-
"""
Test mobilisation module.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from mspray.apps.main.models import Location
from mspray.apps.main.tests.utils import data_setup, load_spray_data
from mspray.apps.main.views.mopup import HealthFacilityMopUpView, MopUpView


class TestMopUpView(TestCase):
    """Test mop-up view."""

    def test_mopup_view(self):
        """Test mop-up view"""
        data_setup()
        factory = RequestFactory()
        request = factory.get("/mop-up")
        view = MopUpView.as_view()
        response = view(request)
        self.assertContains(response, "Mop-up", status_code=200)
        self.assertContains(response, "Lusaka", 1, status_code=200)

        # test targeted
        lusaka = Location.objects.get(name="Lusaka")
        lusaka.target = False
        lusaka.save()
        response = view(request)
        self.assertContains(response, "Lusaka", 0, status_code=200)

    def test_mopup_url(self):
        """Test mop-up URL"""
        self.assertEqual(reverse("mop-up"), "/mop-up")

    def test_health_facility_mopup_view(self):
        """Test HealthFacilityMopUpView"""
        data_setup()
        load_spray_data()

        health_facility = Location.objects.filter(level="RHC").first()
        spray_area = health_facility.get_children().filter(
            name='Akros_2').first()

        factory = RequestFactory()
        request = factory.get("/mopup-up/{}".format(health_facility.parent_id))
        view = HealthFacilityMopUpView.as_view()
        response = view(request, district=health_facility.parent_id)

        self.assertDictEqual(
            {
                'structures_on_ground': 9,
                'visited_sprayed': 5,
                'structures_to_mopup': 3,
                'mopup_days_needed': 0.022222222222222223
            },
            response.context_data['totals']
        )

        self.assertContains(response, health_facility.name, 1, 200)
        self.assertContains(response, spray_area.name, 1, 200)

        self.assertEqual(
            reverse("mop-up", kwargs={"district": health_facility.parent_id}),
            "/mop-up/{}".format(health_facility.parent_id),
        )

        # test targeted
        spray_area.target = False
        spray_area.save()
        view = HealthFacilityMopUpView.as_view()
        response = view(request, district=health_facility.parent_id)
        self.assertContains(response, health_facility.name, 0, 200)
        self.assertContains(response, spray_area.name, 0, 200)

        self.assertDictEqual({
            'structures_on_ground': 0,
            'visited_sprayed': 0,
            'structures_to_mopup': 0,
            'mopup_days_needed': 0
        }, response.context_data['totals'])
