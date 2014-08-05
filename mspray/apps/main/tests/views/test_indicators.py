from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.views.indicators import NumberOfHouseholdsIndicatorView


class TestIndicatorViewSet(TestBase):
    def test_household_list_view(self):
        self._load_area_shapefile()
        self._load_household_shapefile()
        view = NumberOfHouseholdsIndicatorView.as_view()
        request = self.factory.get('/', {'target': 1})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        data = {
            "number_of_households": 502,
            "target_area": "Target Area Chibombo 1"
        }
        self.assertEqual(response.data, data)
