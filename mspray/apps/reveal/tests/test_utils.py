"""module to test reveal utils"""
from django.test import TestCase

from mspray.apps.reveal.utils import add_spray_data


class TestUtils(TestCase):
    """
    Utils test class
    """

    def test_add_spray_data(self):
        """
        Test add_spray_data
        """
        add_spray_data(data={})
        self.fail()
