import os
import mspray

from django.test import TestCase


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
