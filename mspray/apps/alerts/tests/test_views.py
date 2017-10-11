from django.core.urlresolvers import reverse

from mspray.apps.main.tests.test_base import TestBase
from mspray.celery import app


class TestViews(TestBase):

    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_start_health_facility_catchment(self):
        response = self.client.get(reverse('alerts:health_facility_catchment'))
        self.assertEqual(response.status_code, 200)
