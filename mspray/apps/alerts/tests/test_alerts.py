# -*- coding: utf-8 -*-
"""Test alerts module."""
from unittest.mock import patch

from django.test import TestCase

from mspray.apps.alerts.alerts import daily_spray_effectiveness
from mspray.apps.main.tests.utils import data_setup, load_spray_data


class TestAlerts(TestCase):
    """Test alerts functions"""

    @patch("mspray.apps.alerts.alerts.start_flow")
    def test_daily_spray_effectiveness(self, mocked_start_flow):
        """Test daily_spray_effectiveness calls rapidpro"""
        data_setup()
        load_spray_data()
        daily_spray_effectiveness("flow_uuid", '2018-09-20')
        self.assertTrue(mocked_start_flow.called)
        self.assertEqual(mocked_start_flow.call_count, 1)
