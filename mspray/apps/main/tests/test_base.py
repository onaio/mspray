from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from rest_framework.test import APIRequestFactory

from mspray.apps.alerts.rapidpro import RapidProContact
from mspray.apps.main.models import Location
from mspray.apps.main.query import get_location_qs
from mspray.apps.main.serializers import DistrictSerializer


class TestBase(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.factory = APIRequestFactory()

    def _load_fixtures(self):
        call_command(
            "loaddata",
            settings.BASE_DIR + "/mspray/apps/main/tests/fixtures"
            "/20171009/location.json",
            verbosity=0,
        )
        call_command(
            "loaddata",
            settings.BASE_DIR + "/mspray/apps/main/tests/fixtures"
            "/20171009/team_leader.json",
            verbosity=0,
        )
        call_command(
            "loaddata",
            settings.BASE_DIR + "/mspray/apps/main/tests/fixtures"
            "/20171009/team_leader_assistant.json",
            verbosity=0,
        )
        call_command(
            "loaddata",
            settings.BASE_DIR + "/mspray/apps/main/tests/fixtures"
            "/20171009/spray_operator.json",
            verbosity=0,
        )
        call_command(
            "loaddata",
            settings.BASE_DIR + "/mspray/apps/main/tests/fixtures"
            "/20171009/sprayday.json",
            verbosity=0,
        )
        call_command(
            "loaddata",
            settings.BASE_DIR + "/mspray/apps/main/tests/fixtures"
            "/20171009/spraypoint.json",
            verbosity=0,
        )
        call_command(
            "loaddata",
            settings.BASE_DIR + "/mspray/apps/main/tests/fixtures"
            "/20171009/household.json",
            verbosity=0,
        )
        call_command(
            "loaddata",
            settings.BASE_DIR + "/mspray/apps/main/tests/"
            "fixtures/20171009/sprayoperatordailysummary.json",
            verbosity=0,
        )

    def _district_summary_data(self):
        queryset = Location.objects.filter(level="district")
        queryset = (
            get_location_qs(queryset)
            .extra(
                select={
                    "xmin": 'ST_xMin("main_location"."geom")',
                    "ymin": 'ST_yMin("main_location"."geom")',
                    "xmax": 'ST_xMax("main_location"."geom")',
                    "ymax": 'ST_yMax("main_location"."geom")',
                }
            )
            .values(
                "pk",
                "code",
                "level",
                "name",
                "parent",
                "structures",
                "xmin",
                "ymin",
                "xmax",
                "ymax",
                "num_of_spray_areas",
                "num_new_structures",
                "total_structures",
                "visited",
                "sprayed",
            )
        )
        serialized = DistrictSerializer(queryset, many=True)
        return serialized.data

    def _district_summary_totals(self, district_list):
        fields = [
            "structures",
            "visited_total",
            "visited_sprayed",
            "visited_not_sprayed",
            "visited_refused",
            "visited_other",
            "not_visited",
            "found",
            "num_of_spray_areas",
        ]
        totals = {}
        for rec in district_list:
            for field in fields:
                totals[field] = rec[field] + (
                    totals[field] if field in totals else 0
                )
        return totals

    def _get_rapidpro_contact(self):
        name = "Mosh"
        urns = [
            "tel:+254722000000",
            "mailto:one@example.com",
            "mailto:mosh@example.com",
        ]
        return RapidProContact(name=name, raw=urns)
