from unittest.mock import patch

from django.conf import settings

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.sprayday import SprayDayViewSet
from mspray.apps.main.tests.test_tasks import SUBMISSION_DATA, OSMXML
from mspray.celery import app
from mspray.apps.main.models import SprayDay
from mspray.apps.main.models.spray_day import DATA_ID_FIELD


class TestViews(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    @patch('mspray.apps.main.tasks.fetch_osm_xml')
    @patch('mspray.apps.main.utils.run_tasks_after_spray_data')
    def test_create_sprayday(self, tasks_mock, osm_mock):
        view = SprayDayViewSet.as_view({'post': 'create'})

        osm_mock.return_value = OSMXML.strip()

        data = SUBMISSION_DATA
        request = self.factory.post("/api/spraydays", data)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(osm_mock.called)
        self.assertFalse(tasks_mock.called)

    @patch('mspray.apps.main.tasks.fetch_osm_xml')
    @patch('mspray.apps.main.utils.run_tasks_after_spray_data')
    def test_update_sprayday(self, tasks_mock, osm_mock):
        view = SprayDayViewSet.as_view({'post': 'create'})

        # get submission data that has OSM info
        self._load_fixtures()
        sp = SprayDay.objects.filter(
                data__has_key=settings.MSPRAY_OSM_PRESENCE_FIELD).first()
        data_osm = sp.data
        # change the _id field so that we can reuse this data
        data_osm[DATA_ID_FIELD] = 111
        request_osm = self.factory.post("/api/spraydays", data_osm)
        response_osm = view(request_osm)
        self.assertEqual(response_osm.status_code, 201)
        self.assertTrue(tasks_mock.called)
        self.assertTrue(osm_mock.called)
        request_osm2 = self.factory.post("/api/spraydays", data_osm)
        response_osm2 = view(request_osm2)
        self.assertEqual(response_osm2.status_code, 201)
