# -*- coding=utf-8 -*-
"""
Location model module.
"""
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import Q

from mptt.models import MPTTModel, TreeForeignKey


class Location(MPTTModel, models.Model):
    """
    Location model
    """

    name = models.CharField(max_length=255, db_index=1)
    code = models.CharField(max_length=10, db_index=1)
    level = models.CharField(db_index=1, max_length=50)
    parent = TreeForeignKey("self", null=True, on_delete=models.CASCADE)
    structures = models.PositiveIntegerField(default=0)
    pre_season_target = models.PositiveIntegerField(default=0)
    # total number of spray areas, will be zero for spray area location
    num_of_spray_areas = models.PositiveIntegerField(default=0)
    geom = models.MultiPolygonField(srid=4326, null=True)
    data_quality_check = models.BooleanField(default=False)
    average_spray_quality_score = models.FloatField(default=0.0)
    # visited - 20% of the structures have been sprayed in the spray area
    visited = models.PositiveIntegerField(default=0)
    # sprayed - 20% of the structures have been sprayed in the spray area
    sprayed = models.PositiveIntegerField(default=0)
    target = models.BooleanField(default=True)
    is_sensitized = models.BooleanField(null=True)
    is_mobilised = models.BooleanField(null=True)

    class Meta:
        app_label = "main"
        unique_together = ("code", "level", "parent")

    class MPTTMeta:
        level_attr = "mptt_level"

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

    @classmethod
    def get_district_by_code_or_name(cls, name_or_code):
        """
        Returns a District Location object for given name or code.

        Arguments
        ---------
        name_or_code: name or code for the district.
        """
        try:
            return cls.objects.get(code=name_or_code, level="district")
        except cls.DoesNotExist:
            return cls.objects.get(name__iexact=name_or_code, level="district")

    @property
    def health_centers_to_mopup(self):
        """Return the number of Health Centers to Mop-up
        """
        return self.get_children().filter(level="RHC").count()

    @property
    def spray_areas_to_mopup(self):
        """Return the number of Spray Areas to Mop-up
        """
        return self.get_descendants().filter(level="ta").count()

    @property
    def structures_to_mopup(self):
        """Return the number of structures to mopup
        """
        if self.level != "ta":
            return self.spray_areas_to_mopup

        return self.household_set.filter(
            Q(visited=False) | Q(visited__isnull=True)
        ).count()

    @property
    def visited_sprayed(self):
        """Return the number of structures sprayed."""
        return self.sprayday_set.filter(
            sprayable=True, was_sprayed=True
        ).count()

    @property
    def mopup_days_needed(self):
        """Return the number of structures to reach 90% divide by 45"""
        denominator = getattr(settings, "MOPUP_DAYS_DENOMINATOR", 45)
        if self.level != "ta":
            return sum(
                [
                    l.mopup_days_needed
                    for l in self.get_descendants().filter(level="ta")
                ]
            )

        return round(
            self.household_set.filter(
                Q(visited=False) | Q(visited__isnull=True)
            ).count()
            / denominator
        )

    @property
    def not_sprayable(self):
        """Return number of structures that are not sprayable."""
        return self.household_set.filter(sprayable=False).count()

    @property
    def structures_on_ground(self):
        """Return the number of structures on the ground.

        The number of enumerated households (Households count).
        Subtract the number of structures not sprayable.
        Add new structures .
        """
        new_structures = self.sprayday_set.filter(
            sprayable=True, was_sprayed=True, household__isnull=True
        ).count()

        return (
            self.household_set.exclude(sprayable=False).count()
            + new_structures
        )

    @property
    def found(self):
        """Return the number of structures found on the ground

        The number of households visited
        Add number of new structures sprayed.
        """
        new_structures = self.sprayday_set.filter(
            sprayable=True, was_sprayed=True, household__isnull=True
        ).count()

        return (
            self.household_set.filter(sprayable=True, visited=True).count()
            + new_structures
        )

    @property
    def last_visit(self):
        """Return the date of last submission."""
        last_sprayday = self.sprayday_set.last()
        if last_sprayday:
            return last_sprayday.spray_date

        return ""
