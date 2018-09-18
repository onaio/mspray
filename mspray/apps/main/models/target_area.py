# -*- coding: utf-8 -*-
"""
TargetArea model
"""
# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models


class TargetArea(models.Model):
    """
    TargetArea model.
    """
    targetid = models.CharField(db_index=1, max_length=50)
    targeted = models.IntegerField(db_index=1, default=1)
    district_name = models.CharField(max_length=254)
    houses = models.IntegerField(db_index=1)
    geom = models.PolygonField(srid=4326)

    TARGETED_VALUE = 1

    class Meta:
        app_label = "main"

    def __str__(self):
        return "{}_{}".format(self.targetid, self.houses)


# Auto-generated `LayerMapping` dictionary for TargetArea model
targetarea_mapping = {  # pylint: disable=invalid-name
    "targetid": "targetid",
    "predicted": "predicted",
    "predinc": "predinc",
    "ranks": "ranks",
    "houseranks": "houseranks",
    "targeted": "targeted",
    "rank_house": "rank_house",
    "ranked_num": "Ranked_Num",
    "number_of": "Number_of",
    "district_name": "DISTRICT",
    "houses": "Houses",
    "geom": "POLYGON",
}

namibia_mapping = {  # pylint: disable=invalid-name
    "targetid": "UniqueID_1",
    "district_name": "HDist_1",
    "houses": "Count_12",
    "geom": "MULTIPOLYGON",
}
