"""Test reveal app exports"""
from unittest.mock import patch

from django.test import override_settings
from rest_framework.renderers import JSONRenderer

from mspray.apps.main.models import Household, Location
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reveal.export.locations import (export_households,
                                                 export_locations,
                                                 export_rhc_target_areas,
                                                 send_request)
from mspray.apps.reveal.serializers import (HouseholdSerializer,
                                            LocationSerializer)


@override_settings(
    REVEAL_OPENSRP_ACTIVE='Active',
    REVEAL_OPENSRP_BASE_URL="https://example.com",
    REVEAL_OPENSRP_CREATE_PARENT_LOCATIONS_ENDPOINT="add?is_jurisdiction=true",
    REVEAL_OPENSRP_CREATE_STRUCTURE_LOCATIONS_ENDPOINT="add",
    REVEAL_OPENSRP_USERNAME="mosh",
    REVEAL_OPENSRP_PASSWORD="hunter2",
)
class TestExports(TestBase):
    """
    Export test class
    """

    def setUp(self):
        """
        setup test class
        """
        super().setUp()
        self._load_fixtures()

    @patch('mspray.apps.reveal.export.locations.requests.post')
    def test_send_request(self, mock):
        """
        Test send_request
        """
        url = "https://example.com"
        payload = {"foo": "bar"}
        send_request(url, payload, username="mosh", password="hunter2")

        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0], url)
        self.assertDictEqual(kwargs["data"], payload)
        self.assertDictEqual(kwargs["headers"],
                             {'Content-type': 'application/json'})
        self.assertEqual(kwargs["auth"].password, "hunter2")
        self.assertEqual(kwargs["auth"].username, "mosh")

    @patch('mspray.apps.reveal.export.locations.send_request')
    def test_export_locations(self, mock):
        """
        Test export_locations
        """
        location = Location.objects.first()
        queryset = Location.objects.filter(id=location.id)

        export_locations(queryset)

        json_data = JSONRenderer().render([LocationSerializer(location).data])

        mock.assert_called_once_with(
            url="https://example.com/add?is_jurisdiction=true",
            payload=json_data)

    @patch('mspray.apps.reveal.export.locations.send_request')
    def test_export_households(self, mock):
        """
        Test export_households
        """
        location = Location.objects.filter(level='ta').first()
        queryset = Household.objects.filter(location=location)

        export_households(location)

        json_data = JSONRenderer().render(
            [HouseholdSerializer(x).data for x in queryset.iterator()])

        mock.assert_called_once_with(
            url="https://example.com/add",
            payload=json_data)

    @patch('mspray.apps.reveal.export.locations.export_locations')
    def test_export_rhc_target_areas(self, mock):
        """
        Test export_rhc_target_areas
        """
        export_rhc_target_areas(1337)

        args, kwargs = mock.call_args_list[0]
        self.assertEqual(
            list(set(Location.objects.filter(parent__id=1337, target=True))),
            list(set(args[0])))
