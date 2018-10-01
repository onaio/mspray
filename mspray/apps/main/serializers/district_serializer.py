# -*- coding: utf-8 -*-
"""District Serializer module.
"""
from rest_framework import serializers

from mspray.apps.main.models import Location


class DistrictMixin:
    """DistrictMixin class
    """

    def get_targetid(self, obj):  # pylint: disable=no-self-use
        """Return target id."""
        return obj.get("pk") if isinstance(obj, dict) else obj.pk

    def get_district_name(self, obj):  # pylint: disable=no-self-use
        """Return district or location name.
        """
        return obj.get("name") if isinstance(obj, dict) else obj.name

    def get_found(self, obj):  # pylint: disable=no-self-use
        """Return number of spray areas found.
        """
        return obj.get("found") or 0 if isinstance(obj, dict) else obj.found

    def get_visited_total(self, obj):  # pylint: disable=no-self-use
        """Return total number of spray areas visited."""
        # visited_found = count_key_if_percent(
        #     obj, 'sprayed', 20, self.context
        # )
        # return 0  # visited_found
        return obj.get("visited") if isinstance(obj, dict) else obj.visited

    def get_not_visited(self, obj):  # pylint: disable=no-self-use
        """Return number of spray areas not visited."""
        return (
            obj.get("not_visited") or 0
            if isinstance(obj, dict)
            else obj.not_visited
        )

    def get_visited_other(self, obj):  # pylint: disable=no-self-use
        """Return number of spray areas visited other"""
        return (
            obj.get("visited_other") or 0
            if isinstance(obj, dict)
            else obj.visited_other
        )

    def get_visited_refused(self, obj):  # pylint: disable=no-self-use
        """Return number of spray areas visited refused."""
        return (
            obj.get("visited_refused") or 0
            if isinstance(obj, dict)
            else obj.visited_refused
        )

    def get_visited_not_sprayed(self, obj):  # pylint: disable=no-self-use
        """Return number of spray areas visited not sprayed."""
        return (
            obj.get("visited_not_sprayed") or 0
            if isinstance(obj, dict)
            else obj.visited_not_sprayed
        )

    def get_visited_sprayed(self, obj):  # pylint: disable=no-self-use
        """Return number of spray areas visited sprayed."""
        return obj.get("sprayed") if isinstance(obj, dict) else obj.sprayed

    def get_structures(self, obj):  # pylint: disable=no-self-use
        """Return number of enumerated structures in spray areas."""
        return (
            obj.get("structures") if isinstance(obj, dict) else obj.structures
        )

    def get_bounds(self, obj):  # pylint: disable=no-self-use
        """Return bounds [xmin, ymin, xmax, ymax] map extent values."""
        bounds = []
        if obj:
            if isinstance(obj, dict):
                bounds = [
                    obj.get("xmin"),
                    obj.get("ymin"),
                    obj.get("xmax"),
                    obj.get("ymax"),
                ]
            elif obj.geom:
                bounds = list(obj.geom.boundary.extent)

        return bounds

    def get_spray_dates(self, obj):  # pylint: disable=no-self-use
        """Return unique set of dates when spraying was done."""
        if obj:
            # level = obj['level'] if isinstance(obj, dict) else obj.level
            location_id = obj["pk"] if isinstance(obj, dict) else obj.pk
            location = Location.objects.get(pk=location_id)
            queryset = location.visited_district.all()

            return (
                queryset.values_list("spray_date", flat=True)
                .order_by("spray_date")
                .distinct()
            )
        return None


class DistrictSerializer(DistrictMixin, serializers.ModelSerializer):
    """District serializer class."""

    targetid = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    district_pk = serializers.SerializerMethodField()
    rhc = serializers.SerializerMethodField()
    rhc_pk = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
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
    spray_dates = serializers.SerializerMethodField()
    sensitized = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "targetid",
            "district_name",
            "found",
            "structures",
            "visited_total",
            "visited_sprayed",
            "visited_not_sprayed",
            "visited_refused",
            "visited_other",
            "not_visited",
            "bounds",
            "spray_dates",
            "level",
            "num_of_spray_areas",
            "total_structures",
            "district",
            "rhc",
            "district_pk",
            "rhc_pk",
            "num_new_structures",
            "sensitized",
        )
        model = Location

    def get_district(self, obj):  # pylint: disable=no-self-use
        """Return location's district name."""
        if obj:
            return (
                obj.get("parent__parent__name")
                if isinstance(obj, dict)
                else obj.parent.parent.name
            )
        return None

    def get_district_pk(self, obj):  # pylint: disable=no-self-use
        """Return location's district primary key."""
        if obj:
            return (
                obj.get("parent__parent__pk")
                if isinstance(obj, dict)
                else obj.parent.parent.pk
            )
        return None

    def get_rhc(self, obj):  # pylint: disable=no-self-use
        """Return location's health facility name."""
        if obj:
            return (
                obj.get("parent__name")
                if isinstance(obj, dict)
                else obj.parent.name
            )
        return None

    def get_rhc_pk(self, obj):  # pylint: disable=no-self-use
        """Return location's health facility primary key."""
        if obj:
            return (
                obj.get("parent__pk")
                if isinstance(obj, dict)
                else obj.parent.pk
            )
        return None

    def get_sensitized(self, obj):  # pylint: disable=no-self-use
        """Return number of spray areas that have been sensitized."""
        location = obj
        if isinstance(obj, dict):
            location = Location.objects.get(pk=obj["pk"])
        queryset = (
            location.sv_health_facilities
            if location.level == "RHC"
            else location.sv_districts
        )

        return (
            queryset.filter(is_sensitized=True)
            .values("spray_area")
            .distinct()
            .count()
        )
