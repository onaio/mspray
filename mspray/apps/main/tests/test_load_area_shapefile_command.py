from django.core.management import call_command

from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.tests.test_base import TestBase


class TestUtils(TestBase):
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_import_shapefile(self):
        self.skipTest("Model changed no longer applicable.")
        count = TargetArea.objects.count()

        call_command('load_area_shapefile', self.area_shp)

        self.assertTrue(count + 1 == TargetArea.objects.count())
