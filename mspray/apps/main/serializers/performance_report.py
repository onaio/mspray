# -*- coding=utf-8 -*-
"""
PerformanceReportSerializer
"""
from rest_framework import serializers

from mspray.apps.main.models import PerformanceReport


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
