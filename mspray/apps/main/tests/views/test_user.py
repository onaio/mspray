"""Test user login and logout module."""
from unittest.mock import patch
from django.test import TestCase

from mspray.apps.main.views.user import get_form_users

FORM_DATA = {
    "users": [
        {
            "first_name": "Paul",
            "last_name": "Green",
            "user": "paulG",
            "role": "owner",
            "is_org": False
        },
        {
            "first_name": "Cynthia",
            "last_name": "Sale",
            "user": "CSale",
            "role": "owner",
            "is_org": False
        },
        {
            "first_name": "Philip",
            "last_name": "Khali",
            "user": "PKhali",
            "role": "dataentry",
            "is_org": False

        },
        {
            "first_name": "Mary",
            "last_name": "Rose",
            "user": "MRose",
            "role": "owner",
            "is_org": False
        },
        {
            "first_name": "Lucy",
            "last_name": "",
            "user": "lucy",
            "role": "readonly",
            "is_org": False
        },
        {
            "first_name": "Ken",
            "last_name": "Larry",
            "user": "larryK",
            "role": "owner",
            "is_org": False
        },
        {
            "first_name": "Mitchelle",
            "last_name": "Jones",
            "user": "Mjones",
            "role": "readonly",
            "is_org": False
        }]}


class TestUser(TestCase):
    """Test get_form_owners to retrieve form instance."""

    @patch('mspray.apps.main.views.user.fetch_form')
    def test_get_form_users(self, fetch_form_mock):
        """Test fetch form users."""
        fetch_form_mock.return_value = FORM_DATA
        form_id = 361934
        result = [
            'paulG', 'CSale', 'MRose', 'lucy', 'larryK', 'Mjones']

        get_form_users(form_id)

        fetch_form_mock.assert_called()
        self.assertEqual(get_form_users(344713), result)
