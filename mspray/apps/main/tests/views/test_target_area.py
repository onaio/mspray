from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.target_area import TargetAreaViewSet


class TestTargetAreaViewSet(TestBase):
    def test_targetarea_list_view(self):
        self._load_area_shapefile()
        view = TargetAreaViewSet.as_view({'get': 'list'})
        request = self.factory.get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('features', response.data)
        self.assertEqual(response.data['features'][0]['properties']['name'],
                         'Target Area Chibombo 1')
