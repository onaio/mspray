import datetime
import os

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.sprayday import SprayDayViewSet


class TestSprayDayViewSet(TestBase):
    def setUp(self):
        super(TestSprayDayViewSet, self).setUp()
        self.fixtures = ['848_spraypoints']

    def test_spraydays_list_view(self):
        self._loaddata_fixtures(self.fixtures)
        view = SprayDayViewSet.as_view({'get': 'list'})
        request = self.factory.get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        date = datetime.date(2014, 8, 8)
        self.assertEqual(
            response.data['features'][0]['properties']['spray_date'], date)

    def test_spraydays_list_view_ordering(self):
        self._loaddata_fixtures(self.fixtures)
        view = SprayDayViewSet.as_view({'get': 'list'})
        request = self.factory.get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        date = datetime.date(2014, 8, 8)
        self.assertEqual(
            response.data['features'][0]['properties']['spray_date'], date)
        # reverse order
        data = {'ordering': '-spray_date'}
        request = self.factory.get('/', data)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        date = datetime.date(2014, 8, 10)
        self.assertEqual(
            response.data['features'][0]['properties']['spray_date'], date)

    def test_recieve_json_post(self):
        view = SprayDayViewSet.as_view({'post': 'create'})
        count = SprayDay.objects.count()
        path = os.path.join(self.fixtures_dir, '88037_submission.json')

        with open(path) as f:
            data = f.read()
            request = self.factory.post('/', data, 'application/json')
            response = view(request)

            self.assertEqual(response.status_code, 201)
            self.assertEqual(count + 1, SprayDay.objects.count())
