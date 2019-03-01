"""serializers module for Reactive IRS"""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.main.models import Location
from mspray.apps.reactive.irs.mixins import (CHWinLocationMixin,
                                             CHWLocationMixin)


class CHWLocationSerializer(CHWLocationMixin, serializers.ModelSerializer):
    """Community Health Worker (CHW) location serializer class"""

    level = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    code = serializers.ReadOnlyField()
    district_name = serializers.SerializerMethodField()
    structures = serializers.SerializerMethodField()
    total_structures = serializers.SerializerMethodField()
    num_new_structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    spray_dates = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "code",
            "name",
            "district_name",
            "level",
            "found",
            "structures",
            "visited_total",
            "visited_sprayed",
            "visited_not_sprayed",
            "visited_refused",
            "visited_other",
            "not_visited",
            "total_structures",
            "num_new_structures",
            "spray_dates",
            "bounds",
        ]
        model = Location


class GeoCHWLocationSerializer(CHWLocationMixin, GeoFeatureModelSerializer):
    """Geo-aware Community Health Worker (CHW) location serializer class"""

    level = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    code = serializers.ReadOnlyField()
    district_name = serializers.SerializerMethodField()
    structures = serializers.SerializerMethodField()
    total_structures = serializers.SerializerMethodField()
    num_new_structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "code",
            "name",
            "district_name",
            "level",
            "found",
            "structures",
            "visited_total",
            "visited_sprayed",
            "visited_not_sprayed",
            "visited_refused",
            "visited_other",
            "not_visited",
            "total_structures",
            "num_new_structures",
            "bounds",
            "geom",
        ]
        model = Location
        geo_field = "geom"


class CHWinTargetAreaSerializer(CHWinLocationMixin,
                                serializers.ModelSerializer):
    """
    Serializer class for a location that is aware of CHW locations within it
    """

    level = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    code = serializers.ReadOnlyField()
    district_name = serializers.SerializerMethodField()
    structures = serializers.SerializerMethodField()
    total_structures = serializers.SerializerMethodField()
    num_new_structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    spray_dates = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "code",
            "name",
            "district_name",
            "level",
            "found",
            "structures",
            "visited_total",
            "visited_sprayed",
            "visited_not_sprayed",
            "visited_refused",
            "visited_other",
            "not_visited",
            "total_structures",
            "num_new_structures",
            "spray_dates",
            "bounds",
        ]
        model = Location


class GeoCHWinTargetAreaSerializer(CHWinLocationMixin,
                                   GeoFeatureModelSerializer):
    """
    Geo Serializer class for a location that is aware of
    CHW locations within it
    """

    level = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    code = serializers.ReadOnlyField()
    district_name = serializers.SerializerMethodField()
    structures = serializers.SerializerMethodField()
    total_structures = serializers.SerializerMethodField()
    num_new_structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    spray_dates = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "code",
            "name",
            "district_name",
            "level",
            "found",
            "structures",
            "visited_total",
            "visited_sprayed",
            "visited_not_sprayed",
            "visited_refused",
            "visited_other",
            "not_visited",
            "total_structures",
            "num_new_structures",
            "spray_dates",
            "bounds",
            "geom",
        ]
        model = Location
        geo_field = "geom"
