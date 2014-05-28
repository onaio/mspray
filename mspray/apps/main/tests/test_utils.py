from mspray.apps.main import utils
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.tests.test_base import TestBase


class TestUtils(TestBase):
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_import_shapefile(self):
        count = TargetArea.objects.count()

        utils.load_area_layer_mapping(self.area_shp)

        self.assertTrue(count + 1 == TargetArea.objects.count())
