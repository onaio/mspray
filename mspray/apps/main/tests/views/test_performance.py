# -*- coding: utf-8 -*-
"""Test performance views module."""
import datetime
from django.test import RequestFactory, override_settings
from mspray.apps.main.models import (
    Location, PerformanceReport,
    SprayDay, SprayOperator, TeamLeader, TeamLeaderAssistant)
from mspray.apps.main.views.performance import (
    DistrictPerfomanceView, TeamLeadersPerformanceView,
    DISTRICT_PERFORMANCE_SQL, TLA_PERFORMANCE_SQL,
    SOP_PERFORMANCE_SQL, SprayOperatorSummaryView,
    SprayOperatorDailyView)
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.utils import performance_report
from mspray.apps.main.serializers import (
    DistrictPerformanceReportSerializer, TLAPerformanceReportSerializer,
    SprayOperatorPerformanceReportSerializer, PerformanceReportSerializer)
from mspray.apps.main.tests.utils import data_setup


class TestPerformanceView(TestBase):
    """Test performance view class."""

    def test_district_performance(self):
        """Test district performance view.

        This is done by confirming the data received in the response
        context is being aggregated appropriately within the view
        """
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name='Zemba')
        district = rhc.parent
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.save()
        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        """
        Create performance report objects from the different submissions
        made by the particular sprayoperator.
        """
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

        factory = RequestFactory()
        request = factory.get("/")
        view = DistrictPerfomanceView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

        """
        Query obtains all data for the SprayOperator
        including submissions made and passes this to the serializer
        """
        queryset = Location.objects.raw(DISTRICT_PERFORMANCE_SQL)
        serializer = DistrictPerformanceReportSerializer(queryset, many=True)

        self.assertEqual(response.context_data['data'], serializer.data)

    @override_settings(MSPRAY_SUPERVISOR_LABEL='Supervisor')
    def test_team_leader_performance(self):
        """Test team leaders performance view."""
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name='Miti')
        district = rhc.parent
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.save()

        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        """
        Create performance report objects from the different submissions
        made by the particular sprayoperator.
        """
        performance_report(spray_operator)
        report1 = PerformanceReport.objects.get(spray_operator=spray_operator)
        report1.found = 7
        report1.reported_sprayed = 16
        report1.reported_found = 22
        report1.district = rhc
        report1.save()

        report2 = PerformanceReport.objects.get(spray_operator=spray_operator)
        report2.id = None
        report2.sprayformid = 7658
        report2.refused = 6
        report2.found = 12
        report2.reported_sprayed = 6
        report1.district = rhc
        report2.save()

        factory = RequestFactory()
        request = factory.get("/performance/team-leaders/458")
        view = TeamLeadersPerformanceView.as_view()
        response = view(request, slug=district.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Supervisor' in str(response.render().content))

        queryset = TeamLeaderAssistant.objects.raw(
            TLA_PERFORMANCE_SQL, [district.id]
        )
        serializer = TLAPerformanceReportSerializer(queryset, many=True)

        result = {
            'other': 0,
            'refused': 6,
            'sprayed': 2,
            'sprayable': 19,
            'not_sprayable': 0,
            'not_eligible': 0,
            'not_sprayed_total': 6,
            'data_quality_check': False,
            'found_difference': 15,
            'sprayed_difference': 15,
            'no_of_days_worked': 2,
            'avg_structures_per_so': 0.7307692307692307,
            'avg_start_time': datetime.time(16, 22, 17),
            'avg_end_time': datetime.time(16, 38, 8)}

        self.assertEqual(response.context_data['data'], serializer.data)
        self.assertEqual(response.context_data['totals'], result)

    def test_spray_operator_summary_view(self):
        """Test SprayOperatorSummaryView.

        This is done by confirming the data received in the response
        context is being aggregated appropriately within the view
        """
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name='Chadiza_104')
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        team_leader
        spray_operator.rhc = rhc
        spray_operator.save()
        # update spray day object for the particular spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        """
        Create performance report objects from the submissions made
        by the particular sprayoperator.
        """
        performance_report(spray_operator)
        report1 = PerformanceReport.objects.get(spray_operator=spray_operator)
        report1.found = 7
        report1.reported_sprayed = 16
        report1.reported_found = 22
        report1.save()

        report2 = PerformanceReport.objects.get(spray_operator=spray_operator)
        report2.id = None
        report2.sprayformid = 7658
        report2.refused = 6
        report2.found = 12
        report2.reported_sprayed = 6
        report2.save()

        factory = RequestFactory()
        request = factory.get("/performance/spray-operators/2939/102/summary")
        view = SprayOperatorSummaryView.as_view()
        response = view(
            request,
            team_leader=spray_operator.team_leader.id, slug=spray_operator.id)

        self.assertEqual(response.status_code, 200)

        """
        Query obtains all data for the SprayOperator
        including submissions made and passes this to the serializer
        """
        queryset = SprayOperator.objects.raw(
            SOP_PERFORMANCE_SQL, [spray_operator.team_leader_assistant.id]
        )
        serializer = SprayOperatorPerformanceReportSerializer(
            queryset, many=True
        )
        result = {
            'other': 0,
            'refused': 6,
            'sprayed': 2,
            'sprayable': 19,
            'not_sprayable': 0,
            'not_sprayed_total': 6,
            'data_quality_check': False,
            'found_difference': 15,
            'sprayed_difference': 15,
            'no_of_days_worked': 2,
            'avg_structures_per_so': 9.5,
            'avg_start_time': datetime.time(5, 27, 25, 666667),
            'avg_end_time': datetime.time(5, 32, 42, 666667)}

        self.assertEqual(response.context_data['data'], serializer.data)
        self.assertEqual(response.context_data['totals'], result)

    def test__spray_operator_daily_view(self):
        """Test SprayOperatorDailyView.

        This is done by confirming the data received in the response
        context is being aggregated appropriately within the view
        """
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name='John')
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.save()

        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        factory = RequestFactory()
        request = factory.get(
            "/performance/spray-operators/2939/102/538/daily")
        view = SprayOperatorDailyView.as_view()

        """
        Create performance report objects from the submissions made
        by the particular sprayoperator.
        """
        performance_report(spray_operator)
        report1 = PerformanceReport.objects.get(spray_operator=spray_operator)
        report1.found = 7
        report1.reported_sprayed = 16
        report1.reported_found = 22
        report1.save()

        report2 = PerformanceReport.objects.get(spray_operator=spray_operator)
        report2.id = None
        report2.sprayformid = 7658
        report2.refused = 6
        report2.found = 12
        report2.reported_sprayed = 6
        report2.save()

        """
        Query obtains all data for the SprayOperator
        including submissions made and passes this to the serializer
        """
        queryset = PerformanceReport.objects.filter(
            spray_operator=spray_operator
        ).order_by("spray_date")
        serializer = PerformanceReportSerializer(queryset, many=True)
        response = view(
            request, slug=rhc.id,
            team_leader=spray_operator.team_leader.id,
            spray_operator=spray_operator.id)
        self.assertEqual(response.status_code, 200)

        result = {
            'other': 0,
            'refused': 6,
            'sprayed': 2,
            'sprayable': 19,
            'not_sprayable': 0,
            'not_sprayed_total': 6,
            'data_quality_check': False,
            'found_difference': 25,
            'sprayed_difference': 20,
            'avg_start_time': datetime.time(16, 22, 17),
            'avg_end_time': datetime.time(16, 38, 8)}

        self.assertEqual(response.context_data['data'], serializer.data)
        self.assertEqual(
            response.context_data['totals'], result)
