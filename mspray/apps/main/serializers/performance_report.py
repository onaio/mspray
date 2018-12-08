# -*- coding=utf-8 -*-
"""Performance report Serializers."""
from rest_framework import serializers

from django.core.cache import cache
from mspray.apps.main.datetime_tools import average_time
from mspray.apps.main.models import (
    Location,
    PerformanceReport,
    SprayDay,
    SprayOperator,
    TeamLeaderAssistant,
)


class PerformanceReportSerializer(serializers.ModelSerializer):
    """PerformanceReportSerializer"""

    date = serializers.SerializerMethodField()
    sprayable = serializers.IntegerField(source="found")
    sprayed = serializers.IntegerField()
    refused = serializers.IntegerField()
    other = serializers.IntegerField()
    not_sprayed_total = serializers.SerializerMethodField()
    avg_start_time = serializers.SerializerMethodField()
    avg_end_time = serializers.SerializerMethodField()
    data_quality_check = serializers.BooleanField()
    found_difference = serializers.SerializerMethodField()
    sprayed_difference = serializers.SerializerMethodField()
    not_eligible = serializers.IntegerField()

    class Meta:
        fields = (
            "spray_date",
            "found",
            "sprayed",
            "refused",
            "other",
            "start_time",
            "end_time",
            "data_quality_check",
            "reported_found",
            "reported_sprayed",
            "sprayable",
            "found_difference",
            "sprayed_difference",
            "date",
            "avg_start_time",
            "avg_end_time",
            "not_sprayed_total",
            "sprayformid",
            "not_eligible",
            'data'
        )
        model = PerformanceReport

    def get_date(self, obj):  # pylint: disable=no-self-use
        """
        Returns spray_date as date object.
        """
        return obj.spray_date

    def get_avg_start_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns start_time as time object.
        """
        return obj.start_time

    def get_avg_end_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns end_time as time object.
        """
        return obj.end_time

    def get_not_sprayed_total(self, obj):  # pylint: disable=no-self-use
        """
        Returns not sprayed other + refused.
        """
        return obj.other + obj.refused

    def get_found_difference(self, obj):  # pylint: disable=no-self-use
        """
        Returns spray operator found - submitted found difference.
        """
        return obj.reported_found - obj.found

    def get_sprayed_difference(self, obj):  # pylint: disable=no-self-use
        """
        Returns spray operator sprayed - submitted sprayed difference.
        """
        return obj.reported_sprayed - obj.sprayed


class SprayOperatorPerformanceReportSerializer(serializers.ModelSerializer):
    """SprayOperatorPerformanceReportSerializer"""

    sprayable = serializers.SerializerMethodField()
    sprayed = serializers.SerializerMethodField()
    refused = serializers.SerializerMethodField()
    other = serializers.SerializerMethodField()
    not_sprayed_total = serializers.SerializerMethodField()
    avg_start_time = serializers.SerializerMethodField()
    avg_end_time = serializers.SerializerMethodField()
    data_quality_check = serializers.SerializerMethodField()
    found_difference = serializers.SerializerMethodField()
    sprayed_difference = serializers.SerializerMethodField()
    team_leader_assistant_name = serializers.SerializerMethodField()
    spray_operator_code = serializers.CharField(source="code")
    spray_operator_id = serializers.CharField(source="id")
    no_of_days_worked = serializers.IntegerField()
    name = serializers.CharField()
    avg_structures_per_so = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "name",
            "no_of_days_worked",
            "spray_operator_code",
            "spray_operator_id",
            "team_leader",
            "team_leader_assistant_name",
            "sprayed",
            "refused",
            "other",
            "data_quality_check",
            "sprayable",
            "found_difference",
            "sprayed_difference",
            "avg_start_time",
            "avg_end_time",
            "not_sprayed_total",
            "avg_structures_per_so",
        )
        model = SprayOperator

    def get_team_leader_assistant_name(self, obj):  # pylint: disable=R0201
        """Return Team Leader Assistant's name."""
        if obj and obj.team_leader_assistant:
            return obj.team_leader_assistant.name

        return ""

    def get_avg_structures_per_so(self, obj):  # pylint: disable=no-self-use
        """
        Returns ratio of number of structures found over number_of_days_worked.
        """
        if obj.no_of_days_worked == 0:
            return 0

        return obj.found / round(obj.no_of_days_worked)

    def get_sprayable(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures.
        """
        return 0 if obj.found is None else obj.found

    def get_refused(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures not sprayed refused reason.
        """
        return 0 if obj.refused is None else obj.refused

    def get_sprayed(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures sprayed.
        """
        return 0 if obj.sprayed is None else obj.sprayed

    def get_other(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures not sprayed other reason.
        """
        return 0 if obj.other is None else obj.other

    def get_data_quality_check(self, obj):  # pylint: disable=no-self-use
        """
        Returns True or False for all data quality checks for the spray
        operator.
        """

        last_record = (
            PerformanceReport.objects.filter(spray_operator=obj)
            .order_by("spray_date")
            .last()
        )
        if last_record:
            return last_record.data_quality_check

        return True

    def get_avg_start_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns start_time as time object.
        """
        return average_time(
            [
                report.start_time
                for report in obj.performancereport_set.all().only(
                    "start_time"
                )
            ]
        )

    def get_avg_end_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns end_time as time object.
        """
        return average_time(
            [
                report.end_time
                for report in obj.performancereport_set.all().only("end_time")
            ]
        )

    def get_not_sprayed_total(self, obj):  # pylint: disable=no-self-use
        """
        Returns not sprayed other + refused.
        """
        other = obj.other or 0
        refused = obj.refused or 0

        return other + refused

    def get_found_difference(self, obj):  # pylint: disable=no-self-use
        """
        Returns spray operator found - submitted found difference.
        """
        reported_found = 0
        found = 0
        last_record = (
            PerformanceReport.objects.filter(spray_operator=obj)
            .order_by("spray_date")
            .last()
        )
        if last_record:
            reported_found = last_record.reported_found
            found = last_record.found

        return reported_found - found

    def get_sprayed_difference(self, obj):  # pylint: disable=no-self-use
        """
        Returns spray operator sprayed - submitted sprayed difference.
        """
        reported_sprayed = 0
        sprayed = 0
        last_record = (
            PerformanceReport.objects.filter(spray_operator=obj)
            .order_by("spray_date")
            .last()
        )
        if last_record:
            reported_sprayed = last_record.reported_sprayed
            sprayed = last_record.sprayed

        return reported_sprayed - sprayed


class TLAPerformanceReportSerializer(serializers.ModelSerializer):
    """TLAPerformanceReportSerializer"""

    sprayable = serializers.SerializerMethodField()
    sprayed = serializers.SerializerMethodField()
    refused = serializers.SerializerMethodField()
    other = serializers.SerializerMethodField()
    not_sprayed_total = serializers.SerializerMethodField()
    avg_start_time = serializers.SerializerMethodField()
    avg_end_time = serializers.SerializerMethodField()
    data_quality_check = serializers.SerializerMethodField()
    found_difference = serializers.SerializerMethodField()
    sprayed_difference = serializers.SerializerMethodField()
    team_leader_name = serializers.CharField(source="name")
    team_leader_code = serializers.CharField(source="code")
    team_leader_id = serializers.CharField(source="id")
    no_of_days_worked = serializers.IntegerField()
    name = serializers.CharField()
    avg_structures_per_so = serializers.SerializerMethodField()
    not_eligible = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "name",
            "no_of_days_worked",
            "team_leader_code",
            "team_leader_name",
            "team_leader_id",
            "sprayed",
            "not_eligible",
            "refused",
            "other",
            "data_quality_check",
            "sprayable",
            "found_difference",
            "sprayed_difference",
            "avg_start_time",
            "avg_end_time",
            "not_sprayed_total",
            "avg_structures_per_so",
        )
        model = TeamLeaderAssistant

    def get_sprayed(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures sprayed.
        """
        return 0 if obj.sprayed is None else obj.sprayed

    def get_refused(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures not sprayed refused reason.
        """
        return 0 if obj.refused is None else obj.refused

    def get_other(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures not sprayed other reason.
        """
        return 0 if obj.other is None else obj.other

    def get_not_eligible(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures not eligible reason.
        """
        key = "tla-not-eligible-{}".format(obj.pk)
        val = cache.get(key)
        if val is not None:
            return val
        val = (
            SprayDay.objects.filter(
                household__isnull=False,
                household__sprayable=False,
                team_leader_assistant_id=obj.pk,
                sprayable=False,
            )
            .values("osmid")
            .distinct()
            .count()
        )

        cache.set(key, val)

        return val

    def get_avg_structures_per_so(self, obj):  # pylint: disable=no-self-use
        """
        Returns ratio of number of structures found over number_of_days_worked.
        """
        if obj.no_of_days_worked == 0:
            return 0

        return obj.found / round(obj.no_of_days_worked)

    def get_sprayable(self, obj):  # pylint: disable=no-self-use
        """
        Returns number of sprayable structures.
        """
        return obj.found or 0

    def get_data_quality_check(self, obj):  # pylint: disable=no-self-use
        """
        Returns True or False for all data quality checks for the spray
        operator.
        """
        quality_checks = []
        sops = SprayOperator.objects.filter(team_leader_assistant=obj)
        for sop in sops:
            last_record = (
                PerformanceReport.objects.filter(spray_operator=sop)
                .order_by("spray_date")
                .last()
            )
            if last_record:
                quality_checks.append(last_record.data_quality_check)

        return all(quality_checks)

    def get_avg_start_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns start_time as time object.
        """
        return average_time(
            [
                report.start_time
                for report in obj.performancereport_set.all().only(
                    "start_time"
                )
            ]
        )

    def get_avg_end_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns end_time as time object.
        """
        return average_time(
            [
                report.end_time
                for report in obj.performancereport_set.all().only("end_time")
            ]
        )

    def get_not_sprayed_total(self, obj):  # pylint: disable=no-self-use
        """
        Returns not sprayed other + refused.
        """
        other = obj.other or 0
        refused = obj.refused or 0

        return other + refused

    def get_found_difference(self, obj):  # pylint: disable=no-self-use
        """Returns spray operator found - submitted found difference."""
        reported_found = 0
        found = 0

        sops = SprayOperator.objects.filter(team_leader_assistant=obj)
        for sop in sops:
            last_record = (
                PerformanceReport.objects.filter(spray_operator=sop)
                .order_by("spray_date")
                .last()
            )
            if last_record:
                sop_reported_found = last_record.reported_found
                sop_found = last_record.found
                reported_found += sop_reported_found
                found += sop_found

        return reported_found - found

    def get_sprayed_difference(self, obj):  # pylint: disable=no-self-use
        """Returns spray operator sprayed - submitted sprayed difference."""
        reported_sprayed = 0
        sprayed = 0

        sops = SprayOperator.objects.filter(team_leader_assistant=obj)
        for sop in sops:
            last_record = (
                PerformanceReport.objects.filter(spray_operator=sop)
                .order_by("spray_date")
                .last()
            )
            if last_record:
                sop_reported_sprayed = last_record.reported_sprayed
                sop_sprayed = last_record.sprayed
                reported_sprayed += sop_reported_sprayed
                sprayed += sop_sprayed

        return reported_sprayed - sprayed


class DistrictPerformanceReportSerializer(serializers.ModelSerializer):
    """District PerformanceReportSerializer"""

    sprayable = serializers.SerializerMethodField()
    sprayed = serializers.SerializerMethodField()
    refused = serializers.SerializerMethodField()
    other = serializers.SerializerMethodField()
    not_sprayed_total = serializers.SerializerMethodField()
    avg_start_time = serializers.SerializerMethodField()
    avg_end_time = serializers.SerializerMethodField()
    data_quality_check = serializers.SerializerMethodField()
    found_difference = serializers.SerializerMethodField()
    sprayed_difference = serializers.SerializerMethodField()
    spray_operator_code = serializers.CharField(source="code")
    spray_operator_id = serializers.CharField(source="id")
    no_of_days_worked = serializers.IntegerField()
    name = serializers.CharField()
    avg_structures_per_so = serializers.SerializerMethodField()
    not_eligible = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "name",
            "no_of_days_worked",
            "spray_operator_code",
            "spray_operator_id",
            "sprayed",
            "not_eligible",
            "location",
            "refused",
            "other",
            "data_quality_check",
            "sprayable",
            "found_difference",
            "sprayed_difference",
            "avg_start_time",
            "avg_end_time",
            "not_sprayed_total",
            "avg_structures_per_so",
            "success_rate",
        )
        model = Location

    def get_location(self, obj):  # pylint: disable=no-self-use
        """Return the location object."""
        return obj

    def get_avg_structures_per_so(self, obj):  # pylint: disable=no-self-use
        """Ratio of number of structures found over number_of_days_worked."""
        if obj.no_of_days_worked == 0 or obj.no_of_days_worked is None:
            return 0

        return obj.found / round(obj.no_of_days_worked)

    def get_refused(self, obj):  # pylint: disable=no-self-use
        """Return number of sprayable structures refused spraying."""
        return 0 if obj.refused is None else obj.refused

    def get_other(self, obj):  # pylint: disable=no-self-use
        """Return number of sprayable structures not sprayed other reason."""
        return 0 if obj.other is None else obj.other

    def get_not_eligible(self, obj):  # pylint: disable=no-self-use
        """Return number of sprayable structures not eligible reason."""
        key = "performance-not-eligible-{}".format(obj.pk)
        val = cache.get(key)
        if val is not None:
            return val
        val = (
            SprayDay.objects.filter(
                household__isnull=False,
                household__sprayable=False,
                location__parent__parent_id=obj.pk,
                sprayable=False,
            )
            .values("osmid")
            .distinct()
            .count()
        )

        cache.set(key, val)

        return val

    def get_sprayed(self, obj):  # pylint: disable=no-self-use
        """Return number of sprayable structures sprayed."""
        return 0 if obj.p_sprayed is None else obj.p_sprayed

    def get_sprayable(self, obj):  # pylint: disable=no-self-use
        """Returns number of sprayable structures."""
        return 0 if obj.found is None else obj.found

    def get_data_quality_check(self, obj):  # pylint: disable=no-self-use
        """Return True or False for all data quality checks."""

        quality_checks = []
        sops = SprayOperator.objects.filter(
            team_leader_assistant__location=obj
        )
        for sop in sops:
            last_record = (
                PerformanceReport.objects.filter(spray_operator=sop)
                .order_by("spray_date")
                .last()
            )
            if last_record:
                quality_checks.append(last_record.data_quality_check)

        return all(quality_checks)

    def get_avg_start_time(self, obj):  # pylint: disable=no-self-use
        """Return start_time as time object."""
        return average_time(
            [
                report.start_time
                for report in obj.performancereport_set.all().only(
                    "start_time"
                )
                if report.start_time is not None
            ]
        )

    def get_avg_end_time(self, obj):  # pylint: disable=no-self-use
        """Return end_time as time object."""
        return average_time(
            [
                report.end_time
                for report in obj.performancereport_set.all().only("end_time")
                if report.end_time is not None
            ]
        )

    def get_not_sprayed_total(self, obj):  # pylint: disable=no-self-use
        """Return not sprayed other + refused."""
        if obj.other is None or obj.refused is None:
            return 0

        return obj.other + obj.refused

    def get_found_difference(self, obj):  # pylint: disable=no-self-use
        """Return spray operator found - submitted found difference."""
        reported_found = 0
        found = 0

        sops = SprayOperator.objects.filter(
            team_leader_assistant__location=obj
        )
        for sop in sops:
            last_record = (
                PerformanceReport.objects.filter(spray_operator=sop)
                .order_by("spray_date")
                .last()
            )
            if last_record:
                sop_reported_found = last_record.reported_found
                sop_found = last_record.found
                reported_found += sop_reported_found
                found += sop_found

        return reported_found - found

    def get_sprayed_difference(self, obj):  # pylint: disable=no-self-use
        """Return spray operator sprayed - submitted sprayed difference."""
        reported_sprayed = 0
        sprayed = 0

        sops = SprayOperator.objects.filter(
            team_leader_assistant__location=obj
        )
        for sop in sops:
            last_record = (
                PerformanceReport.objects.filter(spray_operator=sop)
                .order_by("spray_date")
                .last()
            )
            if last_record:
                sop_reported_sprayed = last_record.reported_sprayed
                sop_sprayed = last_record.sprayed
                reported_sprayed += sop_reported_sprayed
                sprayed += sop_sprayed

        return reported_sprayed - sprayed

    def get_success_rate(self, obj):  # pylint: disable=no-self-use
        """Return spray operator sprayed - submitted sprayed difference."""
        if obj.sprayed is None or obj.found is None or obj.found == 0:
            return 0

        return (100 * obj.p_sprayed) / obj.found


class RHCPerformanceReportSerializer(DistrictPerformanceReportSerializer):
    """DistrictPerformanceReportSerializer"""

    def get_not_eligible(self, obj):  # pylint: disable=no-self-use
        """Return number of sprayable structures not eligible reason."""
        key = "performance-not-eligible-rhc-{}".format(obj.pk)
        val = cache.get(key)
        if val is not None:
            return val
        val = (
            SprayDay.objects.filter(
                household__isnull=False,
                household__sprayable=False,
                location__parent_id=obj.pk,
                sprayable=False,
            )
            .values("osmid")
            .distinct()
            .count()
        )

        cache.set(key, val)

        return val

    def get_avg_start_time(self, obj):  # pylint: disable=no-self-use
        """Return start_time as time object."""
        return average_time(
            [
                report.start_time
                for report in PerformanceReport.objects.filter(
                    spray_operator__rhc=obj
                ).only("start_time")
                if report.start_time is not None
            ]
        )

    def get_avg_end_time(self, obj):  # pylint: disable=no-self-use
        """Return end_time as time object."""
        return average_time(
            [
                report.end_time
                for report in PerformanceReport.objects.filter(
                    spray_operator__rhc=obj
                ).only("end_time")
                if report.end_time is not None
            ]
        )
