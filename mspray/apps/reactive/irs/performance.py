# -*- coding: utf-8 -*-
"""
Reactive IRS performance dashboard views.
"""
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from mspray.apps.main.datetime_tools import average_time
from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.models import (
    Location,
    PerformanceReport,
    SprayOperator,
    TeamLeaderAssistant,
)
from mspray.apps.main.serializers import (
    DistrictPerformanceReportSerializer,
    PerformanceReportSerializer,
    SprayOperatorPerformanceReportSerializer,
    TLAPerformanceReportSerializer,
)
from mspray.apps.main.views.performance import (
    DISTRICT_PERFORMANCE_SQL,
    SOP_PERFORMANCE_SQL,
    TLA_PERFORMANCE_SQL,
    IsPerformanceViewMixin,
)


# pylint: disable=too-many-ancestors
class DistrictPerfomanceView(IsPerformanceViewMixin, ListView):
    """District perfomance view."""

    model = Location
    template_name = "reactive_irs/performance.html"

    def get_queryset(self):
        """Obtain the queryset."""
        queryset = (
            super(DistrictPerfomanceView, self).get_queryset().filter(target=True)
        )

        return queryset.filter(parent=None).order_by("name")

    def get_context_data(self, **kwargs):
        """Obtain context data."""
        context = super(DistrictPerfomanceView, self).get_context_data(**kwargs)
        districts = Location.objects.filter(parent=None).order_by("name")

        queryset = Location.objects.raw(DISTRICT_PERFORMANCE_SQL)
        serializer = DistrictPerformanceReportSerializer(queryset, many=True)
        num_of_districts = round(districts.count())
        num_of_succes_rates = round(len([i for i in serializer.data]))
        totals = {
            "other": sum((i["other"] for i in serializer.data)),
            "refused": sum((i["refused"] for i in serializer.data)),
            "sprayed": sum((i["sprayed"] for i in serializer.data)),
            "sprayable": sum((i["sprayable"] for i in serializer.data)),
            "not_sprayable": 0,
            "not_eligible": sum((i["not_eligible"] for i in serializer.data)),
            "not_sprayed_total": sum((i["not_sprayed_total"] for i in serializer.data)),
            "data_quality_check": all(
                (i["data_quality_check"] for i in serializer.data)
            ),
            "found_difference": sum((i["found_difference"] for i in serializer.data)),
            "sprayed_difference": sum(
                (i["sprayed_difference"] for i in serializer.data)
            ),
            "pre_season_target": sum(
                (i["location"].pre_season_target for i in serializer.data)
            ),
            "houses": sum((i["location"].structures for i in serializer.data)),
            "no_of_days_worked": sum((i["no_of_days_worked"] for i in serializer.data)),
        }
        totals["avg_structures_per_so"] = (
            (
                sum((i["avg_structures_per_so"] for i in serializer.data))
                / num_of_districts
            )
            if num_of_districts
            else 0
        )
        totals["avg_start_time"] = average_time(
            [i["avg_start_time"] for i in serializer.data if i["avg_start_time"] != ""]
        )
        totals["avg_end_time"] = average_time(
            [i["avg_end_time"] for i in serializer.data if i["avg_start_time"] != ""]
        )
        totals["success_rate"] = (
            (sum((i["success_rate"] for i in serializer.data)) / num_of_succes_rates)
            if num_of_succes_rates
            else 0
        )

        context.update({"data": serializer.data, "totals": totals})
        context.update(DEFINITIONS["performance:district"])

        return context


# pylint: disable=too-many-ancestors,too-few-public-methods
class TeamLeadersPerformanceView(IsPerformanceViewMixin, DetailView):
    """TeamLeaderAssistant performance view."""

    model = Location
    slug_field = "id"
    template_name = "reactive_irs/team-leaders.html"

    def get_context_data(self, **kwargs):
        """Obtain context data."""
        context = super(TeamLeadersPerformanceView, self).get_context_data(**kwargs)
        district = context["object"]

        queryset = TeamLeaderAssistant.objects.raw(TLA_PERFORMANCE_SQL, [district.id])
        serializer = TLAPerformanceReportSerializer(queryset, many=True)

        totals = {
            "other": sum((i["other"] for i in serializer.data)),
            "refused": sum((i["refused"] for i in serializer.data)),
            "sprayed": sum((i["sprayed"] for i in serializer.data)),
            "sprayable": sum((i["sprayable"] for i in serializer.data)),
            "not_sprayable": 0,
            "not_eligible": sum((i["not_eligible"] for i in serializer.data)),
            "not_sprayed_total": sum((i["not_sprayed_total"] for i in serializer.data)),
            "data_quality_check": all(
                (i["data_quality_check"] for i in serializer.data)
            ),
            "found_difference": sum((i["found_difference"] for i in serializer.data)),
            "sprayed_difference": sum(
                (i["sprayed_difference"] for i in serializer.data)
            ),
            "no_of_days_worked": sum((i["no_of_days_worked"] for i in serializer.data)),
            "avg_structures_per_so": (
                sum((i["avg_structures_per_so"] for i in serializer.data))
                / round(
                    TeamLeaderAssistant.objects.filter(location=district).count() or 1
                )
            ),
            "avg_start_time": average_time(
                [
                    i["avg_start_time"]
                    for i in serializer.data
                    if i["avg_start_time"] != ""
                ]
            ),
            "avg_end_time": average_time(
                [i["avg_end_time"] for i in serializer.data if i["avg_end_time"] != ""]
            ),
        }

        context.update(
            {
                "data": serializer.data,
                "totals": totals,
                "district": district,
                "district_name": district.name,
            }
        )
        context.update(DEFINITIONS["tla"])

        return context


# pylint: disable=too-many-ancestors
class SprayOperatorSummaryView(IsPerformanceViewMixin, DetailView):
    """Spray Operator summary performance page."""

    template_name = "reactive_irs/spray-operator-summary.html"
    model = Location
    slug_field = "id"

    def get_context_data(self, **kwargs):
        """Obtain context data."""
        context = super(SprayOperatorSummaryView, self).get_context_data(**kwargs)
        district = context["object"]
        team_leader = self.kwargs.get("team_leader")
        team_leader_assistant = get_object_or_404(TeamLeaderAssistant, pk=team_leader)

        queryset = SprayOperator.objects.raw(
            SOP_PERFORMANCE_SQL, [team_leader_assistant.id]
        )

        serializer = SprayOperatorPerformanceReportSerializer(queryset, many=True)
        totals = {
            "other": sum((i["other"] for i in serializer.data)),
            "refused": sum((i["refused"] for i in serializer.data)),
            "sprayed": sum((i["sprayed"] for i in serializer.data)),
            "sprayable": sum((i["sprayable"] for i in serializer.data)),
            "not_sprayable": 0,
            "not_sprayed_total": sum((i["not_sprayed_total"] for i in serializer.data)),
            "data_quality_check": all(
                (i["data_quality_check"] for i in serializer.data)
            ),
            "found_difference": sum((i["found_difference"] for i in serializer.data)),
            "sprayed_difference": sum(
                (i["sprayed_difference"] for i in serializer.data)
            ),
            "no_of_days_worked": sum((i["no_of_days_worked"] for i in serializer.data)),
            "avg_structures_per_so": sum(
                (i["avg_structures_per_so"] for i in serializer.data)
            ),
            "avg_start_time": average_time(
                [i["avg_start_time"] for i in serializer.data]
            ),
            "avg_end_time": average_time([i["avg_end_time"] for i in serializer.data]),
        }

        context.update(
            {
                "data": serializer.data,
                "totals": totals,
                "team_leader": team_leader,
                "team_leader_name": get_object_or_404(
                    TeamLeaderAssistant, pk=team_leader
                ).name,
                "district": district,
                "district_name": district.name,
            }
        )
        context.update(DEFINITIONS["sop"])

        return context


# pylint: disable=too-many-ancestors
class SprayOperatorDailyView(IsPerformanceViewMixin, DetailView):
    """Spray Operator Daily view."""

    template_name = "reactive_irs/spray-operator-daily.html"
    model = Location
    slug_field = "id"

    def get_context_data(self, **kwargs):
        """Obtain context data."""
        context = super(SprayOperatorDailyView, self).get_context_data(**kwargs)
        district = context["object"]

        team_leader = self.kwargs.get("team_leader")
        spray_operator_id = self.kwargs.get("spray_operator")
        spray_operator = get_object_or_404(SprayOperator, pk=spray_operator_id)
        queryset = PerformanceReport.objects.filter(
            spray_operator=spray_operator
        ).order_by("spray_date")
        serializer = PerformanceReportSerializer(queryset, many=True)
        totals = {
            "other": sum((i["other"] for i in serializer.data)),
            "refused": sum((i["refused"] for i in serializer.data)),
            "sprayed": sum((i["sprayed"] for i in serializer.data)),
            "sprayable": sum((i["sprayable"] for i in serializer.data)),
            "not_sprayable": 0,
            "not_sprayed_total": sum((i["not_sprayed_total"] for i in serializer.data)),
            "data_quality_check": all(
                (i["data_quality_check"] for i in serializer.data)
            ),
            "found_difference": sum((i["found_difference"] for i in serializer.data)),
            "sprayed_difference": sum(
                (i["sprayed_difference"] for i in serializer.data)
            ),
            "avg_start_time": average_time(
                [i["avg_start_time"] for i in serializer.data]
            ),
            "avg_end_time": average_time([i["avg_end_time"] for i in serializer.data]),
        }
        context.update(
            {
                "data": serializer.data,
                "totals": totals,
                "spray_operator": spray_operator.code,
                "spray_operator_name": spray_operator.name,
                "district": district,
                "district_name": district.name,
                "team_leader": team_leader,
                "team_leader_name": spray_operator.team_leader_assistant.name,
            }
        )
        context.update(DEFINITIONS["sop"])

        return context
