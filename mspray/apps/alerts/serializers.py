# -*- coding: utf-8 -*-
"""Alerts serializers."""
from django.conf import settings
from django.contrib.gis.geos import Point

from rest_framework import serializers

from mspray.apps.main.models import Location, SprayDay
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer


class RapidProBaseSerializer(serializers.Serializer):  # pylint: disable=W0223
    """
    Prepares druid data to send to RapidPro
    """

    target_area_id = serializers.IntegerField()
    target_area_name = serializers.CharField()
    rhc_id = serializers.IntegerField()
    rhc_name = serializers.CharField()
    district_id = serializers.IntegerField()
    district_code = serializers.IntegerField()
    district_name = serializers.CharField()
    num_found = serializers.IntegerField(default=0)
    num_sprayed = serializers.IntegerField(default=0)
    spray_coverage = serializers.IntegerField(default=0)
    found_coverage = serializers.IntegerField(default=0)
    spray_effectiveness = serializers.IntegerField(default=0)
    total_structures = serializers.IntegerField(default=0)
    date = serializers.SerializerMethodField()

    def get_date(self, obj):
        """Return a date if set in __init__()."""
        return self.date if self.date and obj else None

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop("date", None)
        super(RapidProBaseSerializer, self).__init__(*args, **kwargs)


class FoundCoverageSerializer(RapidProBaseSerializer):  # pylint: disable=W0223
    """
    Prepares druid data to send to RapidPro
    """

    target_area_id = serializers.SerializerMethodField()
    target_area_name = serializers.SerializerMethodField()
    rhc_id = serializers.SerializerMethodField()
    rhc_name = serializers.SerializerMethodField()
    district_id = serializers.SerializerMethodField()
    district_code = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    has_submissions_today = serializers.IntegerField(default=0)
    today_is_working_day = serializers.IntegerField(default=0)
    total_structures = serializers.SerializerMethodField(default=0)

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop("date", None)
        self.target_area = kwargs.pop("target_area", None)
        super(FoundCoverageSerializer, self).__init__(*args, **kwargs)

    def get_target_area_id(self, data):
        """Return target area id"""
        return data.get("target_area_id") or (
            self.target_area and self.target_area.id
        )

    def get_target_area_name(self, data):
        """Return target area name"""
        return data.get("target_area_name") or (
            self.target_area and self.target_area.name
        )

    def get_rhc_id(self, data):
        """Return Rural Health Center id"""
        return data.get("rhc_id") or (
            self.target_area and self.target_area.parent.id
        )

    def get_rhc_name(self, data):
        """Return Rural Health Center name"""
        return data.get("rhc_name") or (
            self.target_area and self.target_area.parent.name
        )

    def get_district_id(self, data):
        """Return District id"""
        return data.get("district_id") or (
            self.target_area and self.target_area.parent.parent.id
        )

    def get_district_code(self, data):
        """Return District code"""
        return data.get("district_code") or (
            self.target_area and self.target_area.parent.parent.code
        )

    def get_district_name(self, data):
        """Return District name"""
        return data.get("district_name") or (
            self.target_area and self.target_area.parent.parent.name
        )

    def get_total_structures(self, data):
        """Return total number of structures."""
        return data.get("total_structures") or (
            self.target_area and self.target_area.structures
        )


class UserDistanceSerializer(SprayDayDruidSerializer):
    """
    Serliazer for SpraDay object that calculates field between structure
    and user
    """

    target_area_id = serializers.SerializerMethodField()
    target_area_name = serializers.SerializerMethodField()
    rhc_id = serializers.SerializerMethodField()
    rhc_name = serializers.SerializerMethodField()
    district_id = serializers.SerializerMethodField()
    district_code = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    sprayoperator_name = serializers.SerializerMethodField()
    sprayoperator_code = serializers.SerializerMethodField()
    team_leader_assistant_name = serializers.SerializerMethodField()
    team_leader_name = serializers.SerializerMethodField()
    user_latlng = serializers.SerializerMethodField()
    structure_latlng = serializers.SerializerMethodField()
    distance_from_structure = serializers.SerializerMethodField()

    class Meta:
        model = SprayDay
        fields = [
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

    def get_user_latlng(self, obj):  # pylint: disable=no-self-use
        """Return user latlng value"""
        if obj:
            return obj.data.get(settings.MSPRAY_USER_LATLNG_FIELD)
        return None

    def get_structure_latlng(self, obj):  # pylint: disable=no-self-use
        """Return structure latlng value"""
        if obj and obj.geom:
            return "{},{}".format(obj.geom.coords[1], obj.geom.coords[0])
        return None

    def get_distance_from_structure(self, obj):  # pylint: disable=no-self-use
        """Return distance from structure"""
        user_latlng = obj.data.get(settings.MSPRAY_USER_LATLNG_FIELD)
        if obj and obj.geom and user_latlng:
            latlong = [float(x) for x in user_latlng.split(",")]
            user_location = Point(latlong[1], latlong[0])

            return int(user_location.distance(obj.geom))
        return None


class GPSSerializer(SprayDayDruidSerializer):
    """
    Checks whether SprayDay object was created form a submission made when GPS
    was on or off
    """

    target_area_id = serializers.SerializerMethodField()
    target_area_name = serializers.SerializerMethodField()
    rhc_id = serializers.SerializerMethodField()
    rhc_name = serializers.SerializerMethodField()
    district_id = serializers.SerializerMethodField()
    district_code = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    sprayoperator_name = serializers.SerializerMethodField()
    sprayoperator_code = serializers.SerializerMethodField()
    team_leader_assistant_name = serializers.SerializerMethodField()
    team_leader_name = serializers.SerializerMethodField()
    gps_on = serializers.SerializerMethodField()

    class Meta:
        model = SprayDay
        fields = [
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

    def get_gps_on(self, obj):  # pylint: disable=no-self-use
        """
        if settings.MSPRAY_USER_LATLNG_FIELD is missing from data then GPS was
        off when the submission was made
        """
        if obj and settings.MSPRAY_USER_LATLNG_FIELD in obj.data:
            return 1
        return 0


class SprayEffectivenessSerializer(serializers.ModelSerializer):
    """SprayEffectivenessSerializer serializer class."""

    district = serializers.SerializerMethodField()
    spray_area = serializers.SerializerMethodField()
    spray_effectiveness = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ("spray_effectiveness", "district", "spray_area")

    def get_spray_effectiveness(self, obj):  # pylint: disable=no-self-use
        """Return spray_effectiveness."""
        if obj.visited_found:
            return round((obj.visited_sprayed / obj.visited_found) * 100)

        return 0

    def get_spray_area(self, obj):  # pylint: disable=no-self-use
        """Return spray_area name"""
        return obj.name

    def get_district(self, obj):  # pylint: disable=no-self-use
        """Return district id"""
        return obj.parent.parent.code
