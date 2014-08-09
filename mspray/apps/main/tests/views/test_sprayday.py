import os

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.sprayday import SprayDayViewSet


class TestSprayDayViewSet(TestBase):
    def test_spraydays_list_view(self):
        self._load_spraydays_shapefile()
        view = SprayDayViewSet.as_view({'get': 'list'})
        request = self.factory.get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(response.data['features'][0]['properties']['day'],
                         1)

    def test_spraydays_list_view_ordering(self):
        self._load_spraydays_shapefile()
        view = SprayDayViewSet.as_view({'get': 'list'})
        request = self.factory.get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(response.data['features'][0]['properties']['day'],
                         1)
        # reverse order
        data = {'ordering': '-day'}
        request = self.factory.get('/', data)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(response.data['features'][0]['properties']['day'],
                         4)

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
