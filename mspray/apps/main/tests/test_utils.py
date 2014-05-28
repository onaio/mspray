from mspray.apps.main import utils
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.models.household import Household
from mspray.apps.main.tests.test_base import TestBase


class TestUtils(TestBase):
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_import_area_shapefile(self):
        count = TargetArea.objects.count()

        utils.load_area_layer_mapping(self.area_shp)

        self.assertTrue(count + 1 == TargetArea.objects.count())

    def test_import_household_shapefile(self):
        count = Household.objects.count()

        utils.load_household_layer_mapping(self.households_shp)

        self.assertTrue(count + 502 == Household.objects.count())
