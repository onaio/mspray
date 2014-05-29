from django.contrib.gis.utils import LayerMapping

from mspray.apps.main.models.target_area import TargetArea, targetarea_mapping
from mspray.apps.main.models.household import Household, household_mapping
from mspray.apps.main.models.spray_day import SprayDay, sprayday_mapping


def load_layer_mapping(model, shp_file, mapping, verbose=False):
    lm = LayerMapping(model, shp_file, mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


def load_area_layer_mapping(shp_file, verbose=False):
    load_layer_mapping(TargetArea, shp_file, targetarea_mapping, verbose)


def load_household_layer_mapping(shp_file, verbose=False):
    load_layer_mapping(Household, shp_file, household_mapping, verbose)


def load_sprayday_layer_mapping(shp_file, verbose=False):
    load_layer_mapping(SprayDay, shp_file, sprayday_mapping, verbose)
