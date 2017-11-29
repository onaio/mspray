from django.conf import settings
from django.db.models import Count, Sum
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

        queryset = districts.annotate(
            found=Sum('performancereport__found'),
            p_sprayed=Sum('performancereport__sprayed'),
            refused=Sum('performancereport__refused'),
            other=Sum('performancereport__other'),
            reported_found=Sum('performancereport__reported_found'),
            reported_sprayed=Sum('performancereport__reported_sprayed'),
            no_of_days_worked=Count('performancereport'),
            not_eligible=Sum('performancereport__not_eligible'),
        )
        serializer = DistrictPerformanceReportSerializer(queryset, many=True)

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
                round(queryset.count())),
            'avg_start_time': average_time(
                [i['avg_start_time'] for i in serializer.data
                 if i['avg_start_time'] != '']),
            'avg_end_time': average_time([
                i['avg_end_time'] for i in serializer.data
                if i['avg_start_time'] != '']),
            'success_rate': (
                sum([i['success_rate'] for i in serializer.data]) /
                round(len([i for i in serializer.data]))),
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

        queryset = TeamLeaderAssistant.objects.filter(location=district)
        queryset = queryset.annotate(
            found=Sum('performancereport__found'),
            sprayed=Sum('performancereport__sprayed'),
            refused=Sum('performancereport__refused'),
            other=Sum('performancereport__other'),
            reported_found=Sum('performancereport__reported_found'),
            reported_sprayed=Sum('performancereport__reported_sprayed'),
            no_of_days_worked=Count('performancereport'),
            not_eligible=Sum('performancereport__not_eligible'),
        )
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
                round(queryset.count())),
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
        queryset = team_leader_assistant.sprayoperator_set.annotate(
            found=Sum('performancereport__found'),
            sprayed=Sum('performancereport__sprayed'),
            refused=Sum('performancereport__refused'),
            other=Sum('performancereport__other'),
            reported_found=Sum('performancereport__reported_found'),
            reported_sprayed=Sum('performancereport__reported_sprayed'),
            no_of_days_worked=Count('performancereport'),
        )
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
