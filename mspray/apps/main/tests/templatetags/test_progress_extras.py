# -*- coding=utf-8 -*-
"""
Test progress_extras templatetags.
"""
from unittest import TestCase

from mspray.apps.main.templatetags.progress_extras import \
    sprayed_effectively_color


class TestProgressExtras(TestCase):
    """
    Test progress_extras templatetags functions.
    """
    def test_sprayed_effectively_color(self):
        """
        Test sprayed_effectively_color
        """
        value = 90
        self.assertEqual(sprayed_effectively_color(value), 'green')
