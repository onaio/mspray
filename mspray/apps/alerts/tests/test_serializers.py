# -*- coding: utf-8 -*-
"""Test alerts.serializers module."""
from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import TestCase

from rest_framework.utils.serializer_helpers import ReturnDict

from mspray.apps.alerts.serializers import (
    GPSSerializer,
    SprayEffectivenessSerializer,
    UserDistanceSerializer,
)
from mspray.apps.main.models import Location, SprayDay
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.tests.utils import data_setup, load_spray_data


class TestSerializers(TestBase):
    def setUp(self):
        TestBase.setUp(self)
        self._load_fixtures()

    def test_userdistanceserializer(self):
        """
        Ensure that UserDistanceSerializer returns exactly the data that
        we expect
        """
        sprayday = SprayDay.objects.filter(
            data__has_key=settings.MSPRAY_USER_LATLNG_FIELD
        ).first()
        expected_keys = [
            "target_area_id",
            "target_area_name",
            "rhc_id",
            "rhc_name",
            "district_id",
            "district_name",
            "sprayoperator_name",
            "sprayoperator_code",
            "team_leader_assistant_name",
            "team_leader_name",
            "user_latlng",
            "structure_latlng",
            "distance_from_structure",
            "district_code",
        ]

        this_rhc = sprayday.location.get_family().filter(level="RHC").first()
        this_district = (
            sprayday.location.get_family().filter(level="district").first()
        )
        user_latlng = sprayday.data.get(settings.MSPRAY_USER_LATLNG_FIELD)
        structure_latlng = "{},{}".format(
            sprayday.geom.coords[1], sprayday.geom.coords[0]
        )
        # user distance
        if sprayday.data.get(settings.MSPRAY_USER_LATLNG_FIELD):
            latlong = [
                float(x)
                for x in sprayday.data.get(
                    settings.MSPRAY_USER_LATLNG_FIELD
                ).split(",")
            ]
            user_location = Point(latlong[1], latlong[0])
            user_distance = int(user_location.distance(sprayday.geom))
        else:
            latlong = None
            user_location = None
            user_distance = None

        serialized = UserDistanceSerializer(sprayday).data
        self.assertTrue(isinstance(serialized, ReturnDict))
        received_keys = serialized.keys()
        self.assertEqual(len(received_keys), len(expected_keys))
        for key in received_keys:
            self.assertTrue(key in expected_keys)
        self.assertEqual(serialized["target_area_id"], sprayday.location.id)
        self.assertEqual(
            serialized["target_area_name"], sprayday.location.name
        )
        self.assertEqual(serialized["rhc_id"], this_rhc.id)
        self.assertEqual(serialized["rhc_name"], this_rhc.name)
        self.assertEqual(serialized["district_id"], this_district.id)
        self.assertEqual(serialized["district_name"], this_district.name)
        self.assertEqual(serialized["district_code"], this_district.code)
        self.assertEqual(
            serialized["sprayoperator_code"], sprayday.spray_operator.code
        )
        self.assertEqual(
            serialized["sprayoperator_name"], sprayday.spray_operator.name
        )
        if sprayday.team_leader_assistant:
            self.assertEqual(
                serialized["team_leader_assistant_name"],
                sprayday.team_leader_assistant.name,
            )
        else:
            self.assertEqual(serialized["team_leader_assistant_name"], None)
        if sprayday.team_leader:
            self.assertEqual(
                serialized["team_leader_name"], sprayday.team_leader.name
            )
        else:
            self.assertEqual(serialized["team_leader_name"], None)
        self.assertEqual(serialized["user_latlng"], user_latlng)
        self.assertEqual(serialized["structure_latlng"], structure_latlng)
        self.assertEqual(serialized["distance_from_structure"], user_distance)

    def test_gpsserializer(self):
        """
        Ensure that GPSSerializer returns exactly the data that
        we expect
        """
        sprayday = SprayDay.objects.first()
        expected_keys = [
            "target_area_id",
            "target_area_name",
            "rhc_id",
            "rhc_name",
            "district_id",
            "district_name",
            "sprayoperator_name",
            "sprayoperator_code",
            "team_leader_assistant_name",
            "team_leader_name",
            "gps_on",
            "district_code",
        ]

        this_rhc = sprayday.location.get_family().filter(level="RHC").first()
        this_district = (
            sprayday.location.get_family().filter(level="district").first()
        )

        if settings.MSPRAY_USER_LATLNG_FIELD in sprayday.data:
            gps_on = 1
        else:
            gps_on = 0

        serialized = GPSSerializer(sprayday).data
        self.assertTrue(isinstance(serialized, ReturnDict))
        received_keys = serialized.keys()
        self.assertEqual(len(received_keys), len(expected_keys))
        for key in received_keys:
            self.assertTrue(key in expected_keys)
        self.assertEqual(serialized["target_area_id"], sprayday.location.id)
        self.assertEqual(
            serialized["target_area_name"], sprayday.location.name
        )
        self.assertEqual(serialized["rhc_id"], this_rhc.id)
        self.assertEqual(serialized["rhc_name"], this_rhc.name)
        self.assertEqual(serialized["district_id"], this_district.id)
        self.assertEqual(serialized["district_name"], this_district.name)
        self.assertEqual(serialized["district_code"], this_district.code)
        self.assertEqual(
            serialized["sprayoperator_code"], sprayday.spray_operator.code
        )
        self.assertEqual(
            serialized["sprayoperator_name"], sprayday.spray_operator.name
        )
        if sprayday.team_leader_assistant:
            self.assertEqual(
                serialized["team_leader_assistant_name"],
                sprayday.team_leader_assistant.name,
            )
        else:
            self.assertEqual(serialized["team_leader_assistant_name"], None)
        if sprayday.team_leader:
            self.assertEqual(
                serialized["team_leader_name"], sprayday.team_leader.name
            )
        else:
            self.assertEqual(serialized["team_leader_name"], None)
        self.assertEqual(serialized["gps_on"], gps_on)


class TestSprayEffectivenessSerializer(TestCase):
    """Test SprayEffectivenessSerializer"""

    def test_se_serializer(self):
        """Test SprayEffectivenessSerializer"""
        data_setup()
        load_spray_data()
        locations = Location.objects.filter(code="2")
        serializer = SprayEffectivenessSerializer(locations, many=True)
        data = serializer.data[0]
        self.assertEqual(data["spray_effectiveness"], 62)
        self.assertEqual(data["district"], '1')
        self.assertEqual(data["spray_area"], 'Akros_2')
