from django.core.management import call_command

from mspray.apps.main.models.household import Household
from mspray.apps.main.tests.test_base import TestBase


class TestUtils(TestBase):
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_import_shapefile(self):
        self.skipTest("Model changed no longer applicable.")
        count = Household.objects.count()

        call_command('load_household_shapefile', self.households_shp)

        self.assertTrue(count + 502 == Household.objects.count())
