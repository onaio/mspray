from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.household import HouseholdViewSet


class TestHouseholdViewSet(TestBase):
    def setUp(self):
        super(TestHouseholdViewSet, self).setUp()
        self.fixtures = ['target_areas', 'households']
        self.view = HouseholdViewSet.as_view({'get': 'list'})

    def test_household_list_view(self):
        self._loaddata_fixtures(self.fixtures)
        request = self.factory.get('/')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(len(response.data['features']), 100)

    def test_household_list_view_filter_by_target_area(self):
        self._loaddata_fixtures(self.fixtures)
        data = {'target_area': 277}
        request = self.factory.get('/', data)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(len(response.data['features']), 1)

    def test_household_list_view_filter_by_nonexistent_target_area(self):
        self._loaddata_fixtures(self.fixtures)
        data = {'target_area': 21234}
        request = self.factory.get('/', data)
        response = self.view(request)
        self.assertEqual(response.status_code, 404)

    def test_household_list_view_filter_by_invalid_target_area(self):
        self._loaddata_fixtures(self.fixtures)
        data = {'target_area': "dummy"}
        request = self.factory.get('/', data)
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
