import os
import mspray

from django.test import TestCase


class TestBase(TestCase):
    def setUp(self):
        super(TestBase, self).setUp()
        self.area_shp = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(mspray.__file__)),
                'data', 'shapefiles', 'ta-chibombo-1.shp'))
        self.households_shp = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(mspray.__file__)),
                'data', 'shapefiles', 'hh-chimbombo-1.shp'))
