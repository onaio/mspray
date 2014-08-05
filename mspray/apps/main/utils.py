from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.utils import LayerMapping

from mspray.apps.main.models.target_area import TargetArea, targetarea_mapping
from mspray.apps.main.models.household import Household, household_mapping
from mspray.apps.main.models.spray_day import SprayDay, sprayday_mapping
from mspray.apps.main.models.households_buffer import HouseholdsBuffer


def load_layer_mapping(model, shp_file, mapping, verbose=False):
    lm = LayerMapping(model, shp_file, mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


def load_area_layer_mapping(shp_file, verbose=False):
    load_layer_mapping(TargetArea, shp_file, targetarea_mapping, verbose)


def load_household_layer_mapping(shp_file, verbose=False):
    load_layer_mapping(Household, shp_file, household_mapping, verbose)


def load_sprayday_layer_mapping(shp_file, verbose=False):
    load_layer_mapping(SprayDay, shp_file, sprayday_mapping, verbose)


def create_households_buffer():
    distance = 0.00009

    for ta in TargetArea.objects.all():
        hh_buffers = [
            h.geom.buffer(distance)
            for h in Household.objects.filter(geom__coveredby=ta.geom)]
        bf = MultiPolygon(hh_buffers)

        for b in bf.cascaded_union.simplify():
            HouseholdsBuffer.objects.get_or_create(geom=b, target_area=ta)
