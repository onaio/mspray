"""serializer module for reveal app"""
from django.conf import settings

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.main.models import Household, Location


class LocationSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as OpenSRP GeoJSON compatible data """

    status = serializers.SerializerMethodField()
    parentId = serializers.SerializerMethodField()
    geographicLevel = serializers.SerializerMethodField()

    class Meta:
        model = Location
        geo_field = "geom"
        fields = ["id", "name", "status", "parentId", "geographicLevel"]

    def get_status(self, obj):
        """get location_type"""
        if obj:
            return settings.REVEAL_OPENSRP_ACTIVE
        return None

    def get_parentId(self, obj):
        """get parentId"""
        if obj and obj.parent:
            return obj.parent.id
        return None

    def get_geographicLevel(self, obj):
        """get geographicLevel"""
        if obj:
            if obj.level == settings.REVEAL_DISTRICT:
                return settings.REVEAL_OPENSRP_DISTRICT
            if obj.level == settings.REVEAL_RHC:
                return settings.REVEAL_OPENSRP_RHC
            if obj.level == settings.REVEAL_TARGET_AREA:
                return settings.REVEAL_OPENSRP_TARGET_AREA
        return None


class HouseholdSerializer(LocationSerializer):
    """ A class to serialize house holds as OpenSRP GeoJSON compatible data """

    name = serializers.SerializerMethodField()

    class Meta:
        model = Household
        geo_field = "geom"
        fields = ["id", "name", "status", "parentId", "geographicLevel"]

    def get_name(self, obj):  # pylint: disable=unused-argument
        """get name"""
        return None

    def get_parentId(self, obj):
        """get parentId"""
        if obj and obj.location:
            return obj.location.id
        return None

    def get_geographicLevel(self, obj):
        """get geographicLevel"""
        return settings.REVEAL_OPENSRP_HOUSEHOLD
