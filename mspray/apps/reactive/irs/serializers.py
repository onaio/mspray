"""serializers module for Reactive IRS"""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.main.models import Location
from mspray.apps.reactive.irs.mixins import CHWLocationMixin


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
        ]
        model = Location


class GeoCHWLocationSerializer(CHWLocationMixin, GeoFeatureModelSerializer):
    """Geo-aware Community Health Worker (CHW) location serializer class"""

    level = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    code = serializers.ReadOnlyField()
    district_name = serializers.SerializerMethodField()
    structures = serializers.SerializerMethodField()
    total_structures = serializers.IntegerField()
    num_new_structures = serializers.IntegerField()
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
