# -*- coding: utf-8 -*-
"""Test mspray.apps.main.serializers RHCPerformanceReportSerializer."""

from mspray.apps.main.tests.test_base import TestBase

from mspray.apps.main.models import (
    Location,
    SprayOperator,
    TeamLeader,
    Household,
    SprayDay,
    PerformanceReport,
)
from mspray.apps.main.views.performance import RHC_PERFORMANCE_SQL
from mspray.apps.main.tests.utils import data_setup
from mspray.apps.main.utils import performance_report
from mspray.apps.main.serializers import RHCPerformanceReportSerializer


class TestPerformanceSerializer(TestBase):
    """Test Performance Report Serializer module class."""

    def test_rhc_serializer_output(self):
        """Test RHCPerformanceReportSerializer."""
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name="Bwanunkha")
        district = rhc.parent
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = district
        spray_operator.save()

        household = Household.objects.first()
        household.sprayable = True
        household.location = rhc
        household.save()

        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True, household=household)

        performance_report(spray_operator)
        report1 = PerformanceReport.objects.get(spray_operator=spray_operator)
        report1.found = 7
        report1.reported_sprayed = 16
        report1.reported_found = 22
        report1.district = district
        report1.save()

        report2 = PerformanceReport.objects.get(spray_operator=spray_operator)
        report2.id = None
        report2.sprayformid = 7658
        report2.refused = 6
        report2.found = 12
        report2.reported_sprayed = 6
        report1.district = district
        report2.save()

        queryset = Location.objects.raw(RHC_PERFORMANCE_SQL, [district.id])
        serializer_instance = RHCPerformanceReportSerializer(
            queryset, many=True
        )

        expected_fields = [
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
        ]

        self.assertEqual(
            set(expected_fields), set(list(serializer_instance.data[0].keys()))
        )
        self.assertEqual(rhc.id, serializer_instance.data[0]["id"])
        self.assertEqual(19, serializer_instance.data[0]["sprayable"])
        self.assertEqual(
            10.526315789473685, serializer_instance.data[0]["success_rate"]
        )
        self.assertEqual(0, serializer_instance.data[0]["sprayed_difference"])
        self.assertEqual(
            9.5, serializer_instance.data[0]["avg_structures_per_so"]
        )
