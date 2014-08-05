from django.core.management import call_command

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.tests.test_base import TestBase


class TestUtils(TestBase):
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_import_shapefile(self):
        self.skipTest("Model changed no longer applicable.")
        count = SprayDay.objects.count()

        call_command('load_spraydays_shapefile', self.spraydays_shp)

        self.assertTrue(count + 491 == SprayDay.objects.count())
