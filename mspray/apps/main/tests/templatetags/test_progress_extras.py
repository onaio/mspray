# -*- coding=utf-8 -*-
"""
Test progress_extras templatetags.
"""
import datetime
from unittest import TestCase

from mspray.apps.main.templatetags.progress_extras import (
    GREEN,
    ORANGE,
    RED,
    YELLOW,
    decision_date,
    decision_date_colour,
    mopup_days_needed,
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
        self.assertEqual(sprayed_effectively_color(90), GREEN)
        self.assertEqual(sprayed_effectively_color(89), ORANGE)
        self.assertEqual(sprayed_effectively_color(89.9), ORANGE)
        self.assertEqual(sprayed_effectively_color(75), RED)
        self.assertEqual(sprayed_effectively_color(45), RED)
        self.assertEqual(sprayed_effectively_color(20), YELLOW)
        self.assertEqual(sprayed_effectively_color(13), YELLOW)

    def test_structures_mopup_colour(self):
        """Test structures_mopup_colour filter."""
        self.assertEqual(structures_mopup_colour(2), GREEN)
        self.assertEqual(structures_mopup_colour(12), ORANGE)
        self.assertEqual(structures_mopup_colour(24), RED)

    def test_decision_date(self):
        """Test decision_date filter."""
        # less than 2 days after the last visit date
        self.assertEqual(
            decision_date("2018-09-21", datetime.date(2018, 9, 20)),
            "2018-09-21",
        )
        # more than 2 days after the last visit date
        self.assertEqual(
            decision_date("2018-09-25", datetime.date(2018, 9, 20)),
            "No decision form",
        )
        # date of decision form is before the last visit date
        self.assertEqual(
            decision_date("2018-09-15", datetime.date(2018, 9, 20)),
            "No decision form",
        )

    def test_decision_date_colour(self):
        """Test decision_date_colour filter."""
        # less than 2 days after the last visit date
        self.assertEqual(
            decision_date_colour("2018-09-21", datetime.date(2018, 9, 20)), ""
        )
        # more than 2 days after the last visit date
        self.assertEqual(
            decision_date_colour("2018-09-25", datetime.date(2018, 9, 20)), RED
        )
        # date of decision form is before the last visit date
        self.assertEqual(
            decision_date_colour("2018-09-15", datetime.date(2018, 9, 20)), RED
        )

    def test_mopup_days_needed(self):
        """Test mopup_days_needed filter."""
        self.assertEqual(mopup_days_needed(2.6), 3)
        self.assertEqual(mopup_days_needed(0.3), "<1")
        self.assertEqual(mopup_days_needed(0.0), "<1")
