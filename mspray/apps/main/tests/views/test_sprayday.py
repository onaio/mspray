from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.sprayday import SprayDayViewSet


class TestSprayDayViewSet(TestBase):
    def test_household_list_view(self):
        self._load_spraydays_shapefile()
        view = SprayDayViewSet.as_view({'get': 'list'})
        request = self.factory.get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(response.data['features'][0]['properties']['day'],
                         1)
