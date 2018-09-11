from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayOperator
from mspray.apps.main.models import TeamLeaderAssistant
from mspray.apps.main.models.performance_report import PerformanceReport
from mspray.apps.main.serializers import (
    PerformanceReportSerializer, SprayOperatorPerformanceReportSerializer,
    TLAPerformanceReportSerializer, DistrictPerformanceReportSerializer)
from mspray.apps.main.datetime_tools import average_time

HAS_SPRAYABLE_QUESTION = settings.HAS_SPRAYABLE_QUESTION
SPATIAL_QUERIES = settings.MSPRAY_SPATIAL_QUERIES
REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
REASON_REFUSED = settings.MSPRAY_UNSPRAYED_REASON_REFUSED
REASONS = settings.MSPRAY_UNSPRAYED_REASON_OTHER.copy()
REASONS.pop(REASON_REFUSED)
REASON_OTHER = REASONS.keys()
SPRAY_OPERATOR_NAME = settings.MSPRAY_SPRAY_OPERATOR_NAME
SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE
TEAM_LEADER_CODE = settings.MSPRAY_TEAM_LEADER_CODE
TEAM_LEADER_ASSISTANT_CODE = getattr(
    settings, 'MSPRAY_TEAM_LEADER_ASSISTANT_CODE', 'tla_code'
)
TEAM_LEADER_NAME = settings.MSPRAY_TEAM_LEADER_NAME


DISTRICT_PERFORMANCE_SQL = """
SELECT "main_location"."id", "main_location"."name", "main_location"."code", "main_location"."level", "main_location"."parent_id", "main_location"."structures", "main_location"."pre_season_target", "main_location"."num_of_spray_areas", "main_location"."geom", "main_location"."data_quality_check", "main_location"."average_spray_quality_score", "main_location"."visited", "main_location"."sprayed", "main_location"."lft", "main_location"."rght", "main_location"."tree_id", "main_location"."mptt_level", "subq"."found", "subq"."no_of_days_worked", "subq"."reported_sprayed", "subq"."refused", "subq"."reported_found", "subq"."other", "subq"."p_sprayed", "subq"."not_eligible"
FROM
(SELECT "main_location"."id", COALESCE(SUM("main_performancereport"."found"), 0) AS "found", COUNT("main_performancereport"."id") AS "no_of_days_worked", COALESCE(SUM("main_performancereport"."reported_sprayed"), 0) AS "reported_sprayed", COALESCE(SUM("main_performancereport"."refused"), 0) AS "refused", COALESCE(SUM("main_performancereport"."reported_found"), 0) AS "reported_found", COALESCE(SUM("main_performancereport"."other"), 0) AS "other", COALESCE(SUM("main_performancereport"."sprayed"), 0) AS "p_sprayed", COALESCE(SUM("main_performancereport"."not_eligible"), 0) AS "not_eligible" FROM "main_location" LEFT OUTER JOIN "main_performancereport" ON ("main_location"."id" = "main_performancereport"."district_id") WHERE "main_location"."parent_id" IS NULL GROUP BY "main_location"."id") "subq" JOIN "main_location" ON "main_location"."id" = "subq"."id" ORDER BY "main_location"."name" ASC
"""  # noqa

TLA_PERFORMANCE_SQL = """
SELECT "main_teamleaderassistant"."id", "main_teamleaderassistant"."code", "main_teamleaderassistant"."name", "main_teamleaderassistant"."location_id", "main_teamleaderassistant"."data_quality_check", "main_teamleaderassistant"."average_spray_quality_score", "main_teamleaderassistant"."team_leader_id", "subq"."no_of_days_worked", "subq"."found", "subq"."reported_sprayed", "subq"."reported_found", "subq"."not_eligible", "subq"."sprayed", "subq"."other", "subq"."refused"
FROM
(SELECT "main_teamleaderassistant"."id", COUNT("main_performancereport"."id") AS "no_of_days_worked", COALESCE(SUM("main_performancereport"."found"), 0) AS "found", COALESCE(SUM("main_performancereport"."reported_sprayed"), 0) AS "reported_sprayed", COALESCE(SUM("main_performancereport"."reported_found"), 0) AS "reported_found", COALESCE(SUM("main_performancereport"."not_eligible"), 0) AS "not_eligible", COALESCE(SUM("main_performancereport"."sprayed"), 0) AS "sprayed", COALESCE(SUM("main_performancereport"."other"), 0) AS "other", COALESCE(SUM("main_performancereport"."refused"), 0) AS "refused" FROM "main_teamleaderassistant" LEFT OUTER JOIN "main_performancereport" ON ("main_teamleaderassistant"."id" = "main_performancereport"."team_leader_assistant_id") WHERE "main_teamleaderassistant"."location_id" = %s GROUP BY "main_teamleaderassistant"."id") "subq" JOIN "main_teamleaderassistant" on "main_teamleaderassistant"."id" = "subq"."id"
"""  # noqa

SOP_PERFORMANCE_SQL = """
SELECT "main_sprayoperator"."id", "main_sprayoperator"."code", "main_sprayoperator"."name", "main_sprayoperator"."team_leader_id", "main_sprayoperator"."team_leader_assistant_id", "main_sprayoperator"."data_quality_check", "main_sprayoperator"."average_spray_quality_score", "subq"."refused", "subq"."reported_found", "subq"."found", "subq"."other", "subq"."sprayed", "subq"."reported_sprayed", "subq"."no_of_days_worked"
FROM
(SELECT "main_sprayoperator"."id",  COALESCE(SUM("main_performancereport"."refused"), 0) AS "refused", COALESCE(SUM("main_performancereport"."reported_found"), 0) AS "reported_found", COALESCE(SUM("main_performancereport"."found"), 0) AS "found", COALESCE(SUM("main_performancereport"."other"), 0) AS "other", COALESCE(SUM("main_performancereport"."sprayed"), 0) AS "sprayed", COALESCE(SUM("main_performancereport"."reported_sprayed"), 0) AS "reported_sprayed", COUNT("main_performancereport"."id") AS "no_of_days_worked" FROM "main_sprayoperator" LEFT OUTER JOIN "main_performancereport" ON ("main_sprayoperator"."id" = "main_performancereport"."spray_operator_id") WHERE "main_sprayoperator"."team_leader_assistant_id" = %s GROUP BY "main_sprayoperator"."id") "subq" JOIN "main_sprayoperator" on "main_sprayoperator"."id" = "subq"."id"
"""  # noqa


class IsPerformanceViewMixin(SiteNameMixin):
    def get_context_data(self, **kwargs):
        context = super(IsPerformanceViewMixin, self)\
            .get_context_data(**kwargs)
        context['performance_tables'] = True

        return context


class DefinitionAndConditionView(IsPerformanceViewMixin, TemplateView):
    template_name = 'definitions-and-conditions.html'


# pylint: disable=too-many-ancestors
class DistrictPerfomanceView(IsPerformanceViewMixin, ListView):
    """
    District perfomance view
    """
    model = Location
    template_name = 'performance.html'

    def get_queryset(self):
        qs = super(DistrictPerfomanceView, self).get_queryset()

        return qs.filter(parent=None).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(DistrictPerfomanceView, self)\
            .get_context_data(**kwargs)
        districts = Location.objects.filter(parent=None).order_by('name')

        queryset = Location.objects.raw(DISTRICT_PERFORMANCE_SQL)

        serializer = DistrictPerformanceReportSerializer(queryset, many=True)
        num_of_districts = round(districts.count())
        num_of_succes_rates = round(len([i for i in serializer.data]))
        totals = {
            'other': sum([i['other'] for i in serializer.data]),
            'refused': sum([i['refused'] for i in serializer.data]),
            'sprayed': sum([i['sprayed'] for i in serializer.data]),
            'sprayable': sum([i['sprayable'] for i in serializer.data]),
            'not_sprayable': 0,
            'not_eligible': sum([i['not_eligible'] for i in serializer.data]),
            'not_sprayed_total': sum([i['not_sprayed_total']
                                      for i in serializer.data]),
            'data_quality_check': all([i['data_quality_check']
                                       for i in serializer.data]),
            'found_difference': sum([i['found_difference']
                                     for i in serializer.data]),
            'sprayed_difference': sum([i['sprayed_difference'] for i in
                                       serializer.data]),
            'pre_season_target': sum([i['location'].pre_season_target for i in
                                      serializer.data]),
            'houses': sum([i['location'].structures for i in serializer.data]),
            'no_of_days_worked': sum([
                i['no_of_days_worked'] for i in serializer.data]),
            'avg_structures_per_so': (
                sum([i['avg_structures_per_so'] for i in serializer.data]) /
                num_of_districts) if num_of_districts else 0,
            'avg_start_time': average_time(
                [i['avg_start_time'] for i in serializer.data
                 if i['avg_start_time'] != '']),
            'avg_end_time': average_time([
                i['avg_end_time'] for i in serializer.data
                if i['avg_start_time'] != '']),
            'success_rate': (
                sum([i['success_rate'] for i in serializer.data]) /
                num_of_succes_rates) if num_of_succes_rates else 0,
        }
        context.update({
            'data': serializer.data, 'totals': totals
        })
        context.update(DEFINITIONS['performance:district'])

        return context


# pylint: disable=too-many-ancestors
class TeamLeadersPerformanceView(IsPerformanceViewMixin, DetailView):
    """
    TeamLeaderAssistant performance view.
    """
    model = Location
    slug_field = 'id'
    template_name = 'team-leaders.html'

    def get_context_data(self, **kwargs):
        context = super(TeamLeadersPerformanceView, self)\
            .get_context_data(**kwargs)
        district = context['object']

        queryset = TeamLeaderAssistant.objects.raw(TLA_PERFORMANCE_SQL,
                                                   [district.id])

        serializer = TLAPerformanceReportSerializer(queryset, many=True)

        totals = {
            'other': sum([i['other'] for i in serializer.data]),
            'refused': sum([i['refused'] for i in serializer.data]),
            'sprayed': sum([i['sprayed'] for i in serializer.data]),
            'sprayable': sum([i['sprayable'] for i in serializer.data]),
            'not_sprayable': 0,
            'not_eligible': sum([i['not_eligible'] for i in serializer.data]),
            'not_sprayed_total': sum([i['not_sprayed_total']
                                      for i in serializer.data]),
            'data_quality_check': all([i['data_quality_check']
                                       for i in serializer.data]),
            'found_difference': sum([i['found_difference']
                                     for i in serializer.data]),
            'sprayed_difference': sum([i['sprayed_difference'] for i in
                                       serializer.data]),
            'no_of_days_worked': sum([
                i['no_of_days_worked'] for i in serializer.data]),
            'avg_structures_per_so': (
                sum([i['avg_structures_per_so'] for i in serializer.data]) /
                round(TeamLeaderAssistant.objects.filter(
                            location=district).count())),
            'avg_start_time': average_time(
                [i['avg_start_time'] for i in serializer.data
                 if i['avg_start_time'] != '']),
            'avg_end_time': average_time([
                i['avg_end_time'] for i in serializer.data
                if i['avg_end_time'] != '']),
        }

        context.update({
            'data': serializer.data,
            'totals': totals,
            'district': district,
            'district_name': district.name
        })
        context.update(DEFINITIONS['tla'])

        return context


# pylint: disable=too-many-ancestors
class SprayOperatorSummaryView(IsPerformanceViewMixin, DetailView):
    """
    Spray Operator summary performance page.
    """
    template_name = 'spray-operator-summary.html'
    model = Location
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super(SprayOperatorSummaryView, self)\
            .get_context_data(**kwargs)
        district = context['object']
        team_leader = self.kwargs.get('team_leader')
        team_leader_assistant = get_object_or_404(TeamLeaderAssistant,
                                                  code=team_leader)

        queryset = SprayOperator.objects.raw(
            SOP_PERFORMANCE_SQL, [team_leader_assistant.id])

        serializer = SprayOperatorPerformanceReportSerializer(queryset,
                                                              many=True)
        totals = {
            'other': sum([i['other'] for i in serializer.data]),
            'refused': sum([i['refused'] for i in serializer.data]),
            'sprayed': sum([i['sprayed'] for i in serializer.data]),
            'sprayable': sum([i['sprayable'] for i in serializer.data]),
            'not_sprayable': 0,
            'not_sprayed_total': sum([i['not_sprayed_total']
                                      for i in serializer.data]),
            'data_quality_check': all([i['data_quality_check']
                                       for i in serializer.data]),
            'found_difference': sum([i['found_difference']
                                     for i in serializer.data]),
            'sprayed_difference': sum([i['sprayed_difference'] for i in
                                       serializer.data]),
            'no_of_days_worked': sum([
                i['no_of_days_worked'] for i in serializer.data]),
            'avg_structures_per_so': sum([
                i['avg_structures_per_so'] for i in serializer.data]),
            'avg_start_time': average_time(
                [i['avg_start_time'] for i in serializer.data]),
            'avg_end_time': average_time([i['avg_end_time']
                                          for i in serializer.data]),
        }

        context.update(
            {
                'data': serializer.data,
                'totals': totals,
                'team_leader': team_leader,
                'team_leader_name':
                get_object_or_404(TeamLeaderAssistant, code=team_leader).name,
                'district': district,
                'district_name': district.name
            }
        )
        context.update(DEFINITIONS['sop'])

        return context


# pylint: disable=too-many-ancestors
class SprayOperatorDailyView(IsPerformanceViewMixin, DetailView):
    """
    Spray Operator Daily view.
    """
    template_name = 'spray-operator-daily.html'
    model = Location
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super(SprayOperatorDailyView, self)\
            .get_context_data(**kwargs)
        district = context['object']

        team_leader = self.kwargs.get('team_leader')
        spray_operator_code = self.kwargs.get('spray_operator')
        spray_operator = get_object_or_404(SprayOperator,
                                           code=spray_operator_code)
        queryset = PerformanceReport.objects.filter(
            spray_operator=spray_operator).order_by('spray_date')
        serializer = PerformanceReportSerializer(queryset, many=True)
        totals = {
            'other': sum([i['other'] for i in serializer.data]),
            'refused': sum([i['refused'] for i in serializer.data]),
            'sprayed': sum([i['sprayed'] for i in serializer.data]),
            'sprayable': sum([i['sprayable'] for i in serializer.data]),
            'not_sprayable': 0,
            'not_sprayed_total': sum([i['not_sprayed_total']
                                      for i in serializer.data]),
            'data_quality_check': all([i['data_quality_check']
                                       for i in serializer.data]),
            'found_difference': sum([i['found_difference']
                                     for i in serializer.data]),
            'sprayed_difference': sum([i['sprayed_difference'] for i in
                                       serializer.data]),
            'avg_start_time': average_time(
                [i['avg_start_time'] for i in serializer.data]),
            'avg_end_time': average_time([i['avg_end_time']
                                          for i in serializer.data]),
        }
        context.update(
            {
                'data': serializer.data,
                'totals': totals,
                'spray_operator': spray_operator.code,
                'spray_operator_name': spray_operator.name,
                'district': district,
                'district_name': district.name,
                'team_leader': team_leader,
                'team_leader_name': spray_operator.team_leader_assistant.name
            }
        )
        context.update(DEFINITIONS['sop'])

        return context
