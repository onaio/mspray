# -*- coding: utf-8 -*-
"""
Test performance views module.
"""

from django.test import RequestFactory, TestCase
from mspray.apps.main.views.performance import DistrictPerfomanceView
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
