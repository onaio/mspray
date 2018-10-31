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
    decision_date,
    decision_date_colour,
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
