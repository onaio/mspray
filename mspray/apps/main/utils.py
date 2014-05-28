from django.contrib.gis.utils import LayerMapping

from mspray.apps.main.models.target_area import TargetArea, targetarea_mapping


def load_layer_mapping(model, shp_file, mapping, verbose=False):
    lm = LayerMapping(model, shp_file, mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


def load_area_layer_mapping(shp_file, verbose=False):
    load_layer_mapping(TargetArea, shp_file, targetarea_mapping)
