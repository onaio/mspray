# -*- coding=utf-8 -*-
"""
Test progress_extras templatetags.
"""
from unittest import TestCase

from mspray.apps.main.templatetags.progress_extras import (
    GREEN,
    ORANGE,
    RED,
    sprayed_effectively_color,
    structures_mopup_colour,
)


class TestProgressExtras(TestCase):
    """
    Test progress_extras templatetags functions.
    """

    def test_sprayed_effectively_color(self):
        """
        Test sprayed_effectively_color
        """
        value = 90
        self.assertEqual(sprayed_effectively_color(value), "green")

    def test_structures_mopup_colour(self):
        """Test structures_mopup_colour filter."""
        self.assertEqual(structures_mopup_colour(2), GREEN)
        self.assertEqual(structures_mopup_colour(12), ORANGE)
        self.assertEqual(structures_mopup_colour(24), RED)
