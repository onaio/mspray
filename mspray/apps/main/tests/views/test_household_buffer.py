from django.shortcuts import urlresolvers

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.household_buffer import HouseholdBufferViewSet


class TestHouseholdBufferViewSet(TestBase):
    def setUp(self):
        super(TestHouseholdBufferViewSet, self).setUp()
        self.fixtures = ['target_areas', 'households']
        self.view = HouseholdBufferViewSet.as_view({'get': 'list'})

    def test_list_view(self):
        request = self.factory.get('/')
        self.fixtures = [
            '848_households', '848_target_area', '848_spraypoints']
        self._create_households_buffer(self.fixtures)
        data = {'target_area': 848}
        request = self.factory.get('/', data)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(len(response.data['features']), 36)

    def test_link(self):
        try:
            urlresolvers.resolve('/buffers')
        except:
            self.fail("Cannot resolve url /buffers")
