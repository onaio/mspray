from unittest.mock import patch

from django.core.urlresolvers import reverse

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import Location, TeamLeader
from mspray.apps.alerts.views import start_health_facility_catchment
from mspray.apps.alerts.views import start_so_daily_form_completion
from mspray.celery import app


class TestViews(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    @patch('mspray.apps.alerts.views.health_facility_catchment_hook')
    def test_start_health_facility_catchment(self, mock):
        """
        We are testing that the start_health_facility_catchment view is working
        and that it calls the health_facility_catchment_hook task
        """
        request = self.factory.get(reverse('alerts:health_facility_catchment'))
        response = start_health_facility_catchment(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock.delay.called)

    @patch('mspray.apps.alerts.views.so_daily_form_completion')
    def test_start_so_daily_form_completion(self, mock):
        """
        We want to test that the view "start_so_daily_form_completion":
            - gives a 200 reponse when POSted to
            - calles the 'so_daily_form_completion' taks with the right args
        """
        self._load_fixtures()
        district = Location.objects.filter(level='district').first()
        tla = TeamLeader.objects.first()
        post_data = {'district': district.code, 'SO_name': tla.code,
                     'confirmdecisionform': "No"}
        request = self.factory.post(reverse('alerts:so_daily_form_completion'),
                                    data=post_data)
        response = start_so_daily_form_completion(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock.delay.called)
        args, kwargs = mock.delay.call_args_list[0]
        self.assertEqual(args[0], str(district.code))
        self.assertEqual(args[1], str(tla.code))
        self.assertEqual(args[2], "No")
