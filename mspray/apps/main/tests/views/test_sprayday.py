import datetime
import os

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.sprayday import SprayDayViewSet


class TestSprayDayViewSet(TestBase):
    def setUp(self):
        super(TestSprayDayViewSet, self).setUp()
        self.fixtures = ['848_spraypoints']
        self.view = SprayDayViewSet.as_view({
            'post': 'create',
            'get': 'list'
        })

    def test_spraydays_dates_only_view(self):
        self._loaddata_fixtures(self.fixtures)
        data = {'dates_only': 'true'}
        request = self.factory.get('/', data)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        date = datetime.date(2014, 8, 8)
        self.assertIn(date, response.data)
        self.assertEqual(len(response.data), 3)

    def test_spraydays_list_view(self):
        self._loaddata_fixtures(self.fixtures)
        request = self.factory.get('/')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        date = datetime.date(2014, 8, 8)
        self.assertEqual(
            response.data['features'][0]['properties']['spray_date'], date)

    def test_spraydays_list_view_ordering(self):
        self._loaddata_fixtures(self.fixtures)
        request = self.factory.get('/')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        date = datetime.date(2014, 8, 8)
        self.assertEqual(
            response.data['features'][0]['properties']['spray_date'], date)
        # reverse order
        data = {'ordering': '-spray_date'}
        request = self.factory.get('/', data)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        date = datetime.date(2014, 8, 10)
        self.assertEqual(
            response.data['features'][0]['properties']['spray_date'], date)

    def test_recieve_json_post(self):
        count = SprayDay.objects.count()
        path = os.path.join(self.fixtures_dir, '88037_submission.json')

        with open(path) as f:
            data = f.read()
            request = self.factory.post('/', data, 'application/json')
            response = self.view(request)

            self.assertEqual(response.status_code, 201)
            self.assertEqual(count + 1, SprayDay.objects.count())

            # test double entry, should not add
            request = self.factory.post('/', data, 'application/json')
            response = self.view(request)

            self.assertEqual(count + 1, SprayDay.objects.count())
            self.assertEqual(response.status_code, 201)

    def test_recieve_json_post_missing_date(self):
        count = SprayDay.objects.count()
        path = os.path.join(self.fixtures_dir,
                            '88037_submission_missing_date.json')

        with open(path) as f:
            data = f.read()
            request = self.factory.post('/', data, 'application/json')
            response = self.view(request)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(count, SprayDay.objects.count())

    def test_recieve_json_post_missing_data_id(self):
        count = SprayDay.objects.count()
        path = os.path.join(self.fixtures_dir,
                            '88037_submission_missing_data_id.json')

        with open(path) as f:
            data = f.read()
            request = self.factory.post('/', data, 'application/json')
            response = self.view(request)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(count, SprayDay.objects.count())

    def test_recieve_json_post_missing_gps_field(self):
        count = SprayDay.objects.count()
        path = os.path.join(self.fixtures_dir,
                            '88037_submission_missing_gps_field.json')

        with open(path) as f:
            data = f.read()
            request = self.factory.post('/', data, 'application/json')
            response = self.view(request)

            self.assertEqual(response.status_code, 400)
            self.assertEqual(count, SprayDay.objects.count())

    def test_recieve_json_post_non_structure_gps(self):
        count = SprayDay.objects.count()
        path = os.path.join(self.fixtures_dir,
                            '88037_submission_non_structure_gps_field.json')

        with open(path) as f:
            data = f.read()
            request = self.factory.post('/', data, 'application/json')
            response = self.view(request)

            self.assertEqual(response.status_code, 201)
            self.assertEqual(count + 1, SprayDay.objects.count())

            request = self.factory.get('/')
            response = self.view(request)
            self.assertEqual(response.status_code, 200)
            data = {'features': [], 'type': 'FeatureCollection'}
            self.assertEqual(response.data, data)
