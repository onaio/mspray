from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.household import HouseholdViewSet


class TestHouseholdViewSet(TestBase):
    def test_household_list_view(self):
        self._load_household_shapefile()
        view = HouseholdViewSet.as_view({'get': 'list'})
        request = self.factory.get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(response.data['features'][0]['properties']['name'],
                         '3033')
