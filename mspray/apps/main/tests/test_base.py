import os
import mspray

from django.test import TestCase, RequestFactory

from mspray.apps.main import utils
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.models.household import Household
from mspray.apps.main.models.spray_day import SprayDay


class TestBase(TestCase):
    def setUp(self):
        super(TestBase, self).setUp()
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(mspray.__file__)),
            'data'
        )
        self.area_shp = os.path.abspath(
            os.path.join(data_dir, 'shapefiles', 'ta-chibombo-1.shp'))
        self.households_shp = os.path.abspath(
            os.path.join(data_dir, 'shapefiles', 'hh-chimbombo-1.shp'))
        self.spraydays_shp = os.path.abspath(
            os.path.join(data_dir, 'shapefiles', 'spray-days.shp'))

        self.factory = RequestFactory()

    def _load_area_shapefile(self):
        count = TargetArea.objects.count()
        utils.load_area_layer_mapping(self.area_shp, verbose=True)
        self.assertTrue(count + 1 == TargetArea.objects.count())

    def _load_household_shapefile(self):
        count = Household.objects.count()
        utils.load_household_layer_mapping(self.households_shp, verbose=True)
        self.assertTrue(count + 502 == Household.objects.count())

    def _load_spraydays_shapefile(self):
        count = SprayDay.objects.count()
        utils.load_sprayday_layer_mapping(self.spraydays_shp, verbose=True)
        self.assertTrue(count + 491 == SprayDay.objects.count())
