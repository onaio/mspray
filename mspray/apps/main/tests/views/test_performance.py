# -*- coding: utf-8 -*-
"""Test performance views module."""
import datetime

from django.test import RequestFactory, override_settings

from mspray.apps.main.models import (
    Location,
    PerformanceReport,
    SprayDay,
    SprayOperator,
    TeamLeader,
    TeamLeaderAssistant,
)
from mspray.apps.main.serializers import (
    DistrictPerformanceReportSerializer,
    MDADistrictPerformanceReportSerializer,
    PerformanceReportSerializer,
    TLAPerformanceReportSerializer,
)
from mspray.apps.main.serializers.performance_report import (
    RHCPerformanceReportSerializer,
    SprayOperatorPerformanceReportSerializer,
)
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.tests.utils import data_setup
from mspray.apps.main.utils import performance_report
from mspray.apps.main.views.performance import (
    DISTRICT_PERFORMANCE_SQL,
    SOP_PERFORMANCE_SQL,
    TLA_PERFORMANCE_SQL,
    DistrictPerfomanceView,
    MDADistrictPerfomanceView,
    MDASprayOperatorDailyView,
    MDASprayOperatorSummaryView,
    RHCPerformanceView,
    SprayOperatorDailyView,
    SprayOperatorSummaryView,
    TeamLeadersPerformanceView,
)


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
        rhc = Location.objects.get(name="Zemba")
        district = rhc.parent
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = rhc.parent
        spray_operator.save()
        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        # Create performance report objects from the submissions made
        # by the particular sprayoperator.

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

        # Query obtains all data for the SprayOperator
        # including submissions made and passes this to the serializer

        queryset = Location.objects.raw(DISTRICT_PERFORMANCE_SQL)
        serializer = DistrictPerformanceReportSerializer(queryset, many=True)

        self.assertEqual(response.context_data["data"], serializer.data)

    def test_mda_district_performance(self):
        """Test district performance view.

        This is done by confirming the data received in the response
        context is being aggregated appropriately within the view
        """
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name="Zemba")
        district = rhc.parent
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = rhc.parent
        spray_operator.save()
        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        # Create performance report objects from the submissions made
        # by the particular sprayoperator.

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
        view = MDADistrictPerfomanceView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # Query obtains all data for the SprayOperator
        # including submissions made and passes this to the serializer

        queryset = Location.performance_queryset('sop_district', None)
        serializer = MDADistrictPerformanceReportSerializer(
            queryset, many=True
        )

        self.assertEqual(response.context_data["data"], serializer.data)

    @override_settings(MSPRAY_SUPERVISOR_LABEL="Supervisor")
    def test_team_leader_performance(self):
        """Test team leaders performance view."""
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name="Miti")
        district = rhc.parent
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = rhc.parent
        spray_operator.save()

        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        # Create performance report objects from the submissions made
        # by the particular sprayoperator.

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

        request = RequestFactory().get("/performance/team-leaders/458")
        view = TeamLeadersPerformanceView.as_view()
        response = view(request, slug=district.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Supervisor" in str(response.render().content))

        queryset = TeamLeaderAssistant.objects.raw(
            TLA_PERFORMANCE_SQL, [district.id]
        )
        serializer = TLAPerformanceReportSerializer(queryset, many=True)

        result = {
            "other": 0,
            "refused": 6,
            "sprayed": 2,
            "sprayable": 19,
            "not_sprayable": 0,
            "not_eligible": 0,
            "not_sprayed_total": 6,
            "data_quality_check": False,
            "found_difference": 15,
            "sprayed_difference": 15,
            "no_of_days_worked": 2,
            "avg_structures_per_so": 0.7307692307692307,
            "avg_start_time": datetime.time(16, 22, 17),
            "avg_end_time": datetime.time(16, 38, 8),
        }

        self.assertEqual(response.context_data["data"], serializer.data)
        self.assertEqual(response.context_data["totals"], result)

    def test_spray_operator_summary_view(self):  # pylint: disable=C0103
        """Test SprayOperatorSummaryView.

        This is done by confirming the data received in the response
        context is being aggregated appropriately within the view
        """
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name="Chadiza_104")
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = rhc.parent
        spray_operator.save()
        # update spray day object for the particular spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        # Create performance report objects from the submissions made
        # by the particular sprayoperator.

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
            team_leader=spray_operator.team_leader.id,
            slug=spray_operator.id,
        )

        self.assertEqual(response.status_code, 200)

        # Query obtains all data for the SprayOperator
        # including submissions made and passes this to the serializer

        queryset = SprayOperator.objects.raw(
            SOP_PERFORMANCE_SQL, [spray_operator.team_leader_assistant.id]
        )
        serializer = SprayOperatorPerformanceReportSerializer(
            queryset, many=True
        )
        result = {
            "other": 0,
            "refused": 6,
            "sprayed": 2,
            "sprayable": 19,
            "not_sprayable": 0,
            "not_sprayed_total": 6,
            "data_quality_check": False,
            "found_difference": 15,
            "sprayed_difference": 15,
            "no_of_days_worked": 2,
            "avg_structures_per_so": 9.5,
            "avg_start_time": datetime.time(5, 27, 25, 666667),
            "avg_end_time": datetime.time(5, 32, 42, 666667),
        }

        self.assertEqual(response.context_data["data"], serializer.data)
        self.assertEqual(response.context_data["totals"], result)

    def test__spray_operator_daily_view(self):
        """Test SprayOperatorDailyView.

        This is done by confirming the data received in the response
        context is being aggregated appropriately within the view
        """
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name="John")
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = rhc.parent
        spray_operator.save()

        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        factory = RequestFactory()
        request = factory.get(
            "/performance/spray-operators/2939/102/538/daily"
        )
        view = SprayOperatorDailyView.as_view()

        # Create performance report objects from the submissions made
        # by the particular sprayoperator.

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

        # Query obtains all data for the SprayOperator
        # including submissions made and passes this to the serializer

        queryset = PerformanceReport.objects.filter(
            spray_operator=spray_operator
        ).order_by("spray_date")
        serializer = PerformanceReportSerializer(queryset, many=True)
        response = view(
            request,
            slug=rhc.id,
            team_leader=spray_operator.team_leader.id,
            spray_operator=spray_operator.id,
        )
        self.assertEqual(response.status_code, 200)

        result = {
            "other": 0,
            "refused": 6,
            "sprayed": 2,
            "sprayable": 19,
            "not_sprayable": 0,
            "not_sprayed_total": 6,
            "data_quality_check": False,
            "found_difference": 25,
            "sprayed_difference": 20,
            "avg_start_time": datetime.time(16, 22, 17),
            "avg_end_time": datetime.time(16, 38, 8),
        }

        self.assertEqual(response.context_data["data"], serializer.data)
        self.assertEqual(response.context_data["totals"], result)

    def test_mda_spray_operator_summary_view(self):  # pylint: disable=C0103
        """Test MDASprayOperatorSummaryView.

        This is done by confirming the data received in the response
        context is being aggregated appropriately within the view
        """
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name="Chadiza_104")
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        # next we identify a SprayDay object for the spray operator
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = rhc.parent
        spray_operator.save()

        # update spray day object for the particular spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        # Create performance report objects from the submissions made
        # by the particular sprayoperator.

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
        request = factory.get("spray-operators/2/summary")
        view = MDASprayOperatorSummaryView.as_view()

        response = view(request, rhc_id=rhc.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["rhc_name"], "Chadiza_104")

        # Query obtains all data for the SprayOperator
        # including submissions made and passes this to the serializer

        serializer = SprayOperatorPerformanceReportSerializer(
            response.context_data["spray_operator_qs"], many=True
        )

        result = {
            "other": 0,
            "refused": 6,
            "sprayed": 2,
            "sprayable": 19,
            "not_sprayable": 0,
            "not_sprayed_total": 6,
            "data_quality_check": False,
            "found_difference": 15,
            "sprayed_difference": 15,
            "no_of_days_worked": 2,
            "avg_structures_per_so": 9.5,
            "avg_start_time": datetime.time(16, 22, 17),
            "avg_end_time": datetime.time(16, 38, 8),
            "custom": {},
            "not_eligible": 0,
        }

        self.assertEqual(response.context_data["totals"], result)
        self.assertEqual(response.context_data["data"], serializer.data)

    def test_mda_spray_operator_daily_view(self):  # pylint: disable=C0103
        """Test MDASprayOperatorDailyView.

        This is done by confirming the data received in the response
        context is being aggregated appropriately within the view
        """
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name="John")
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = rhc.parent
        spray_operator.save()
        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        factory = RequestFactory()
        request = factory.get("/mda/performance/spray-operators/33/42/daily")
        view = MDASprayOperatorDailyView.as_view()

        # Create performance report objects from the submissions made
        # by the particular sprayoperator.

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

        # Query obtains all data for the SprayOperator
        # including submissions made and passes this to the serializer

        queryset = PerformanceReport.objects.filter(
            spray_operator=spray_operator
        ).order_by("spray_date")
        serializer = PerformanceReportSerializer(queryset, many=True)

        response = view(
            request, rhc_id=rhc.id, spray_operator=spray_operator.id
        )
        self.assertEqual(response.status_code, 200)

        result = {
            "other": 0,
            "refused": 6,
            "sprayed": 2,
            "sprayable": 19,
            "not_sprayable": 0,
            "not_sprayed_total": 6,
            "data_quality_check": False,
            "found_difference": 25,
            "sprayed_difference": 20,
            "avg_start_time": datetime.time(16, 22, 17),
            "avg_end_time": datetime.time(16, 38, 8),
            "data": {},
            "not_eligible": 0,
        }

        self.assertEqual(response.context_data["rhc_name"], "John")
        self.assertEqual(response.context_data["data"], serializer.data)
        self.assertEqual(response.context_data["totals"], result)

    def test_rhc_performance_view(self):
        """Test RHCPerformanceView."""
        # first we load our test data
        data_setup()
        self._load_fixtures()
        rhc = Location.objects.get(name="Zemba")
        district = rhc.parent
        spray_operator = SprayOperator.objects.first()
        team_leader = TeamLeader.objects.first()
        spray_operator.team_leader = team_leader
        spray_operator.rhc = rhc
        spray_operator.district = district
        spray_operator.save()
        # next we identify a SprayDay object for the spray operator
        spray_day = SprayDay.objects.filter(spray_operator=spray_operator)
        spray_day.update(sprayable=True)

        # Create performance report objects from the submissions made
        # by the particular sprayoperator.

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

        request = RequestFactory().get("/mda/performance/rhcs/2")
        view = RHCPerformanceView.as_view()
        response = view(request, district_id=district.id)
        self.assertEqual(response.status_code, 200)

        # Query obtains all data for the SprayOperator
        # including submissions made and passes this to the serializer

        queryset = Location.performance_queryset("sop_rhc", district)
        serializer = RHCPerformanceReportSerializer(queryset, many=True)

        result = {
            "custom": {},
            "days_worked": 1,
            "other": 0,
            "refused": 6,
            "sprayed": 2,
            "sprayable": 19,
            "not_sprayable": 0,
            "not_eligible": 0,
            "not_sprayed_total": 6,
            "data_quality_check": True,
            "found_difference": 0,
            "sprayed_difference": 0,
            "houses": 26,
            "no_of_days_worked": 2,
            "avg_structures_per_so": 0.4523809523809524,
            "avg_start_time": datetime.time(16, 22, 17),
            "avg_end_time": datetime.time(16, 38, 8),
            "success_rate": 0.0,
        }

        self.assertEqual(response.context_data["totals"], result)
        self.assertEqual(response.context_data["data"], serializer.data)
