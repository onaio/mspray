# -*- coding:utf-8 -*-
"""
common_tags module.
"""
from django.conf import settings


DATA_ID_FIELD = getattr(settings, "MSPRAY_DATA_ID_FIELD", "_id")
SENSITIZED_FIELD = getattr(
    settings, "SENSITIZED_FIELD", "osmstructure:sensitized"
)
SENSITIZATION_OSM_FIELD = getattr(
    settings, "SENSITIZATION_OSM_FIELD", "osmstructure"
)
