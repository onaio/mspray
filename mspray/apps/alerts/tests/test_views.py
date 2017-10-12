from django.core.urlresolvers import reverse

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.alerts.views import start_health_facility_catchment
from mspray.celery import app


class TestViews(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_start_health_facility_catchment(self):
        request = self.factory.get(reverse('alerts:health_facility_catchment'))
        response = start_health_facility_catchment(request)
        self.assertEqual(response.status_code, 200)
