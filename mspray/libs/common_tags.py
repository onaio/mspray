# -*- coding:utf-8 -*-
"""common_tags module."""
from django.conf import settings

DATA_ID_FIELD = getattr(settings, "MSPRAY_DATA_ID_FIELD", "_id")
SENSITIZED_FIELD = getattr(
    settings, "SENSITIZED_FIELD", "osmstructure:sensitized"
)
SENSITIZATION_OSM_FIELD = getattr(
    settings, "SENSITIZATION_OSM_FIELD", "osmstructure"
)
MOBILISED_FIELD = getattr(
    settings, "MOBILISED_FIELD", "osmstructure:mobilized"
)
MOBILISATION_OSM_FIELD = getattr(
    settings, "MOBILISATION_OSM_FIELD", "osmstructure"
)

SPRAY_AREA_FIELD = "spray_area"
MOBILISATION_LONGITUDE_FIELD = getattr(
    settings, "MOBILISATION_LONGITUDE_FIELD", "osmstructure:ctr:lon")
MOBILISATION_LATITUDE_FIELD = getattr(
    settings, "MOBILISATION_LATITUDE_FIELD", "osmstructure:ctr:lat")
