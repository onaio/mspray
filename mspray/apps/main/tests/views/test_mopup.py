# -*- coding: utf-8 -*-
"""
Test mobilisation module.
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from mspray.apps.main.views.mopup import MopUpView


class TestMopUpView(TestCase):
    """Test mop-up view."""

    def test_mopup_view(self):
        """Test mop-up view"""
        factory = RequestFactory()
        request = factory.get("/mop-up")
        view = MopUpView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_mopup_url(self):
        """Test mop-up URL"""
        self.assertEqual(reverse("mop-up"), "/mop-up")
