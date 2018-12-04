# -*- coding: utf-8 -*-
"""
Test performance views module.
"""
import datetime
from django.test import RequestFactory, override_settings
from mspray.apps.main.models import (
    Location, PerformanceReport,
    SprayDay, SprayOperator, TeamLeader)
from mspray.apps.main.views.performance import (
    DistrictPerfomanceView, TeamLeadersPerformanceView,
    DISTRICT_PERFORMANCE_SQL)
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.utils import performance_report
from mspray.apps.main.serializers import DistrictPerformanceReportSerializer
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
        import pdb; pdb.set_trace()
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
            'pre_season_target': 70000,
            'houses': 102356,
            'no_of_days_worked': 2,
            'avg_structures_per_so': 1.3571428571428572,
            'avg_start_time': datetime.time(16, 22, 17),
            'avg_end_time': datetime.time(16, 38, 8),
            'success_rate': 1.5037593984962407}

        self.assertEqual(response.context_data['totals'], result)
        self.assertEqual(response.context_data['data'], serializer.data)

    @override_settings(MSPRAY_SUPERVISOR_LABEL='Supervisor')
    def test_team_leader_performance(self):
        """Test team leaders performance view."""
        data_setup()
        sprayarea = Location.objects.get(name='Akros_1')

        factory = RequestFactory()
        request = factory.get("/performance/team-leaders/458")
        view = TeamLeadersPerformanceView.as_view()
        response = view(request, slug=sprayarea.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Supervisor' in str(response.render().content))
