# -*- coding: utf-8 -*-
"""
Test performance views module.
"""

from django.test import RequestFactory, TestCase, override_settings
from mspray.apps.main.models import Location
from mspray.apps.main.views.performance import (
    DistrictPerfomanceView, TeamLeadersPerformanceView)
from mspray.apps.main.tests.utils import data_setup


class TestPerformanceView(TestCase):
    """Test performance view class."""

    def test_district_performance(self):
        """Test district performance view."""
        data_setup()
        factory = RequestFactory()
        request = factory.get("/")
        view = DistrictPerfomanceView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(
        MSPRAY_TEAM_LEADER_ASSISTANT='supervisor'
    )
    def test_team_leader_performance(self):
        """Test team leaders performance view."""
        data_setup()
        sprayarea = Location.objects.get(name='Akros_1')

        factory = RequestFactory()
        request = factory.get("/performance/team-leaders/458")
        view = TeamLeadersPerformanceView.as_view()
        response = view(request, slug=sprayarea.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('supervisor' in str(response.render().content))
