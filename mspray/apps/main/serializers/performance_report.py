# -*- coding=utf-8 -*-
"""
PerformanceReportSerializer
"""
from rest_framework import serializers

from mspray.apps.main.models import (
    PerformanceReport, SprayOperator, TeamLeaderAssistant)
from mspray.apps.main.datetime_tools import average_time


class PerformanceReportSerializer(serializers.ModelSerializer):
    """
    PerformanceReportSerializer
    """
    date = serializers.SerializerMethodField()
    sprayable = serializers.IntegerField(source='found')
    sprayed = serializers.IntegerField()
    refused = serializers.IntegerField()
    other = serializers.IntegerField()
    not_sprayed_total = serializers.SerializerMethodField()
    avg_start_time = serializers.SerializerMethodField()
    avg_end_time = serializers.SerializerMethodField()
    data_quality_check = serializers.BooleanField()
    found_difference = serializers.SerializerMethodField()
    sprayed_difference = serializers.SerializerMethodField()

    class Meta:
        fields = ('spray_date', 'found', 'sprayed', 'refused', 'other',
                  'start_time', 'end_time', 'data_quality_check',
                  'reported_found', 'reported_sprayed', 'sprayable',
                  'found_difference', 'sprayed_difference', 'date',
                  'avg_start_time', 'avg_end_time', 'not_sprayed_total',
                  'sprayformid')
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
    """
    PerformanceReportSerializer
    """
    sprayable = serializers.SerializerMethodField()
    sprayed = serializers.IntegerField()
    refused = serializers.IntegerField()
    other = serializers.IntegerField()
    not_sprayed_total = serializers.SerializerMethodField()
    avg_start_time = serializers.SerializerMethodField()
    avg_end_time = serializers.SerializerMethodField()
    data_quality_check = serializers.SerializerMethodField()
    found_difference = serializers.SerializerMethodField()
    sprayed_difference = serializers.SerializerMethodField()
    team_leader_assistant_name = serializers.CharField(
        source='team_leader_assistant.name')
    spray_operator_code = serializers.CharField(source='code')
    no_of_days_worked = serializers.IntegerField()
    name = serializers.CharField()
    avg_structures_per_so = serializers.SerializerMethodField()

    class Meta:
        fields = ('name', 'no_of_days_worked', 'spray_operator_code',
                  'team_leader', 'team_leader_assistant_name', 'sprayed',
                  'refused', 'other', 'data_quality_check', 'sprayable',
                  'found_difference', 'sprayed_difference', 'avg_start_time',
                  'avg_end_time', 'not_sprayed_total', 'avg_structures_per_so')
        model = SprayOperator

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
        return obj.found

    def get_data_quality_check(self, obj):  # pylint: disable=no-self-use
        """
        Returns True or False for all data quality checks for the spray
        operator.
        """

        return all([
            report.data_quality_check
            for report in obj.performancereport_set.all().only(
                'data_quality_check')
        ])

    def get_avg_start_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns start_time as time object.
        """
        return average_time([
            report.start_time
            for report in obj.performancereport_set.all().only('start_time')
        ])

    def get_avg_end_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns end_time as time object.
        """
        return average_time([
            report.end_time
            for report in obj.performancereport_set.all().only('end_time')
        ])

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


class TLAPerformanceReportSerializer(serializers.ModelSerializer):
    """
    PerformanceReportSerializer
    """
    sprayable = serializers.SerializerMethodField()
    sprayed = serializers.IntegerField()
    refused = serializers.IntegerField()
    other = serializers.IntegerField()
    not_sprayed_total = serializers.SerializerMethodField()
    avg_start_time = serializers.SerializerMethodField()
    avg_end_time = serializers.SerializerMethodField()
    data_quality_check = serializers.SerializerMethodField()
    found_difference = serializers.SerializerMethodField()
    sprayed_difference = serializers.SerializerMethodField()
    team_leader_name = serializers.CharField(source='name')
    spray_operator_code = serializers.CharField(source='code')
    no_of_days_worked = serializers.IntegerField()
    name = serializers.CharField()
    avg_structures_per_so = serializers.SerializerMethodField()
    not_eligible = serializers.IntegerField()

    class Meta:
        fields = ('name', 'no_of_days_worked', 'spray_operator_code',
                  'team_leader', 'team_leader_name', 'sprayed', 'not_eligible',
                  'refused', 'other', 'data_quality_check', 'sprayable',
                  'found_difference', 'sprayed_difference', 'avg_start_time',
                  'avg_end_time', 'not_sprayed_total', 'avg_structures_per_so')
        model = TeamLeaderAssistant

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
        return obj.found

    def get_data_quality_check(self, obj):  # pylint: disable=no-self-use
        """
        Returns True or False for all data quality checks for the spray
        operator.
        """

        return all([
            report.data_quality_check
            for report in obj.performancereport_set.all().only(
                'data_quality_check')
        ])

    def get_avg_start_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns start_time as time object.
        """
        return average_time([
            report.start_time
            for report in obj.performancereport_set.all().only('start_time')
        ])

    def get_avg_end_time(self, obj):  # pylint: disable=no-self-use
        """
        Returns end_time as time object.
        """
        return average_time([
            report.end_time
            for report in obj.performancereport_set.all().only('end_time')
        ])

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
