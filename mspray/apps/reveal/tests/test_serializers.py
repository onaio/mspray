"""module to test reveal Serializers"""
import json
from collections import OrderedDict

from django.contrib.gis.geos import GEOSGeometry
from django.test import override_settings

from mspray.apps.main.models import Household, Location
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reveal.serializers import (HouseholdSerializer,
                                            LocationSerializer)


@override_settings(REVEAL_OPENSRP_ACTIVE="Active")
class TestSerializers(TestBase):
    """
    Serializers test class
    """

    def setUp(self):
        """
        setup test class
        """
        super().setUp()
        self._load_fixtures()

    def test_location_serializer(self):
        """
        Test reveal LocationSerializer
        """
        location = Location.objects.filter(level="district").first()
        serializer = LocationSerializer(location)
        data = serializer.data

        for key in ["id", "type", "geometry", "properties"]:
            self.assertTrue(key in data.keys())

        self.assertEqual(location.id, data["id"])
        self.assertEqual("Feature", data["type"])
        self.assertEqual("MultiPolygon", data["geometry"]["type"])

        self.assertDictEqual(
            OrderedDict(
                [
                    ("name", "Chadiza"),
                    ("status", "Active"),
                    ("parentId", None),
                    ("geographicLevel", 0),
                ]
            ),
            data["properties"],
        )

    def test_household_serializer(self):
        """
        test reveal HouseholdSerializer
        """
        house = Household.objects.get(id=1)
        serializer = HouseholdSerializer(house)
        data = serializer.data

        for key in ["id", "type", "geometry", "properties"]:
            self.assertTrue(key in data.keys())

        self.assertEqual(house.id, data["id"])
        self.assertEqual("Feature", data["type"])
        self.assertEqual("Polygon", data["geometry"]["type"])

        self.assertEqual(
            house.bgeom, GEOSGeometry(json.dumps(data["geometry"])))

        self.assertDictEqual(
            OrderedDict(
                [
                    ("name", None),
                    ("status", "Active"),
                    ("parentId", house.location.id),
                    ("geographicLevel", 4),
                ]
            ),
            data["properties"],
        )
