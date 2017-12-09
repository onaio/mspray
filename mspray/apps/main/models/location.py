# -*- coding=utf-8 -*-
"""
Location model module.
"""
from django.contrib.gis.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Location(MPTTModel, models.Model):
    """
    Location model
    """
    name = models.CharField(max_length=255, db_index=1)
    code = models.PositiveIntegerField()
    level = models.CharField(db_index=1, max_length=50)
    parent = TreeForeignKey('self', null=True, on_delete=models.CASCADE)
    structures = models.PositiveIntegerField(default=0)
    pre_season_target = models.PositiveIntegerField(default=0)
    # total number of spray areas, will be zero for spray area location
    num_of_spray_areas = models.PositiveIntegerField(default=0)
    geom = models.MultiPolygonField(srid=4326, null=True)
    objects = models.GeoManager()
    data_quality_check = models.BooleanField(default=False)
    average_spray_quality_score = models.FloatField(default=0.0)
    # visited - 20% of the structures have been sprayed in the spray area
    visited = models.PositiveIntegerField(default=0)
    # sprayed - 20% of the structures have been sprayed in the spray area
    sprayed = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'main'
        unique_together = ('code', 'level', 'parent')

    class MPTTMeta:
        level_attr = 'mptt_level'

    def __str__(self):
        return self.name

    @property
    def district_name(self):
        """
        Location name.
        """
        return self.name

    @property
    def targetid(self):
        """
        Locaton code
        """
        return self.code

    @property
    def houses(self):
        """
        Number of structures in location.
        """
        return self.structures
