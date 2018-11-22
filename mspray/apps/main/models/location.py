# -*- coding=utf-8 -*-
"""
Location model module.
"""
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.db.models.functions import Cast
from django.utils.functional import cached_property

from mptt.models import MPTTModel, TreeForeignKey

from mspray.libs.common_tags import MOBILISED_FIELD, SENSITIZED_FIELD


class Location(MPTTModel, models.Model):  # pylint: disable=R0904
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
    priority = models.PositiveIntegerField(null=True)

    class Meta:
        app_label = "main"
        unique_together = ("code", "level", "parent")

    class MPTTMeta:
        level_attr = "mptt_level"

    def __str__(self):
        return self.name

    @cached_property
    def district_name(self):
        """
        Location name.
        """
        return self.name

    @cached_property
    def targetid(self):
        """
        Locaton code
        """
        return self.code

    @cached_property
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

    @cached_property
    def health_centers_to_mopup(self):
        """Return the number of Health Centers to Mop-up
        """
        return self.get_children().filter(level="RHC", target=True).count()

    @cached_property
    def spray_areas_to_mopup(self):
        """Return the number of Spray Areas to Mop-up
        """
        return sum(
            1
            for l in self.get_descendants().filter(level="ta", target=True)
            if l.structures_to_mopup > 0
        )

    @cached_property
    def structures_to_mopup(self):
        """Return the number of structures to mopup

        Number of structures remaining to be sprayed to reach 90% spray
        effectiveness.
        """
        if self.level != "ta":
            return sum(
                l.structures_to_mopup
                for l in self.get_descendants().filter(level="ta", target=True)
            )

        key = "structures-to-mopup-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        mopup_percentage = getattr(settings, "MOPUP_PERCENTAGE", 90)
        ninetieth_percentile = round(
            (mopup_percentage / 100) * self.structures_on_ground
        )
        if self.visited_sprayed >= ninetieth_percentile:
            val = 0
        else:
            val = ninetieth_percentile - self.visited_sprayed

        cache.set(key, val)

        return val

    @cached_property
    def visited_sprayed(self):
        """Return the number of structures sprayed."""
        if self.level != "ta":
            return sum(
                l.visited_sprayed
                for l in self.get_descendants().filter(level="ta", target=True)
            )

        key = "visited-sprayed-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = self.sprayday_set.filter(
            sprayable=True, was_sprayed=True
        ).count()
        cache.set(key, val)

        return val

    @cached_property
    def mopup_days_needed(self):
        """Return the number of structures to reach 90% divide by 45"""
        denominator = getattr(settings, "MOPUP_DAYS_DENOMINATOR", 45)
        if self.level != "ta":
            return sum(
                [
                    l.mopup_days_needed
                    for l in self.get_descendants().filter(
                        level="ta", target=True
                    )
                ]
            )

        key = "mopup-days-needed-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = (
            self.household_set.filter(
                Q(visited=False) | Q(visited__isnull=True)
            ).count()
            / denominator
        )
        cache.set(key, val)

        return val

    @cached_property
    def not_sprayable(self):
        """Return number of structures that are not sprayable."""

        key = "not-sprayable-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = self.household_set.filter(sprayable=False).count()
        cache.set(key, val)

        return val

    @cached_property
    def new_structures(self):
        """Return number of new structures that have been sprayed."""
        if self.level != "ta":
            return sum(
                l.new_structures
                for l in self.get_descendants().filter(level="ta", target=True)
            )
        key = "new-structures-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = self.sprayday_set.filter(
            Q(spraypoint__isnull=False)
            | Q(spraypoint__isnull=True, was_sprayed=True),
            sprayable=True,
            household__isnull=True,
        ).count()
        cache.set(key, val)

        return val

    @cached_property
    def duplicates(self):
        """Return number of duplicates structures that have been sprayed."""
        key = "duplicates-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        agg = (
            self.sprayday_set.filter(was_sprayed=True)
            .exclude(household__isnull=True)
            .values("household")
            .distinct()
            .annotate(duplicates=Count("household") - 1)
            .aggregate(total_duplicates=Sum("duplicates"))
        )

        val = agg.get("total_duplicates") if agg.get("total_duplicates") else 0
        cache.set(key, val)

        return val

    @cached_property
    def structures_on_ground(self):
        """Return the number of structures on the ground.

        The number of enumerated households (Households count).
        Subtract the number of structures not sprayable.
        Add new structures .
        """
        if self.level != "ta":
            return sum(
                l.structures_on_ground
                for l in self.get_descendants().filter(level="ta", target=True)
            )

        key = "structures-on-ground-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = (
            self.household_set.exclude(sprayable=False).count()
            + self.new_structures
            + self.duplicates
        )
        cache.set(key, val)

        return val

    @cached_property
    def visited_found(self):
        """Return the number of structures found on the ground

        The number of households visited
        Add number of new structures sprayed.
        """
        if self.level != "ta":
            return sum(
                l.visited_found
                for l in self.get_descendants().filter(level="ta", target=True)
            )

        key = "visited-found-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        new_structures = self.sprayday_set.filter(
            sprayable=True, was_sprayed=True, household__isnull=True
        ).count()

        val = (
            self.household_set.filter(sprayable=True, visited=True).count()
            + new_structures
            + self.duplicates
        )
        cache.set(key, val)

        return val

    @cached_property
    def last_visit(self):
        """Return the date of last submission."""
        key = "last-visit-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        last_sprayday = self.sprayday_set.last()
        if last_sprayday:
            val = last_sprayday.spray_date
            cache.set(key, val)

            return val

        return ""

    @cached_property
    def last_decision_date(self):
        """Return the date of last decision report."""
        key = "last-decision-date-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        decision = self.decision_spray_areas.last()  # pylint: disable=E1101
        if decision:
            val = decision.data.get("today")
            cache.set(key, val)

            return val

        return ""

    @cached_property
    def mobilised(self):
        """Return mobilisation status"""
        sensitized = self.mb_spray_areas.first()  # pylint: disable=no-member
        if sensitized:
            return sensitized.data.get(MOBILISED_FIELD)
        return ""

    @cached_property
    def sensitized(self):
        """Return sensitization status"""
        sensitized = self.sv_spray_areas.first()  # pylint: disable=no-member
        if sensitized:
            return sensitized.data.get(SENSITIZED_FIELD)
        return ""

    @cached_property
    def mda_structures(self):
        """Return the number of MDA structures on the ground."""
        if self.level != "ta":
            return sum(
                l.mda_structures
                for l in self.get_descendants().filter(level="ta", target=True)
            )

        key = "mda-structures-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = (
            self.household_set.exclude(sprayable=False).count()
            + self.new_structures
            + self.duplicates
        )
        cache.set(key, val)

        return val

    @cached_property
    def mda_found(self):
        """Return the number of MDA structures found on the ground.i

        ('mda_status'='all_received' + 'mda_status'=some_received' +
        'mda_status'=none_received')
        """
        if self.level != "ta":
            return sum(
                l.mda_found
                for l in self.get_descendants().filter(level="ta", target=True)
            )

        key = "mda-found-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = (
            self.household_set.filter(sprayable=True, visited=True).count()
            + self.new_structures
            + self.duplicates
        )
        cache.set(key, val)

        return val

    @cached_property
    def mda_received(self):
        """Return the number of MDA structures received.

        ('mda_status'='all_received' +'mda_status'=some_received')
        """
        if self.level != "ta":
            return sum(
                l.mda_received
                for l in self.get_descendants().filter(level="ta", target=True)
            )

        key = "mda-received-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = self.sprayday_set.filter(
            sprayable=True, was_sprayed=True
        ).count()
        cache.set(key, val)

        return val

    @cached_property
    def mda_none_received(self):
        """Return the number of MDA structures none received.

        ('mda_status'='none_received')
        """
        if self.level != "ta":
            return sum(
                l.mda_none_received
                for l in self.get_descendants().filter(level="ta", target=True)
            )

        key = "mda-received-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = (
            self.sprayday_set.filter(sprayable=True, was_sprayed=False)
            .values("osmid")
            .distinct()
            .count()
        )
        cache.set(key, val)

        return val

    @cached_property
    def mda_spray_areas(self):
        """Return the number of MDA Spray Areas
        """
        key = "mda-spray-areas-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        val = self.get_descendants().filter(level="ta", target=True).count()
        cache.set(key, val)

        return val

    @cached_property
    def mda_received_percentage(self):
        """Return percentage of received over eligible structures."""
        return (
            0
            if self.mda_structures == 0
            else (self.mda_received * 100) / self.mda_structures
        )

    @cached_property
    def mda_spray_areas_found(self):
        """Return the number of MDA Spray Areas."""
        key = "mda-spray-areas-found-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val
        sprayed_found_percentage = getattr(
            settings, "SPRAYED_FOUND_PERCENTAGE", 20
        )

        val = sum(
            1
            for spray_area in self.get_descendants().filter(
                level="ta", target=True
            )
            if spray_area.mda_received_percentage >= sprayed_found_percentage
        )
        cache.set(key, val)

        return val

    @cached_property
    def mda_spray_areas_received(self):
        """Return the number of MDA spray areas received.

        ('mda_status'='all_received' +'mda_status'=some_received')
        """

        key = "mda-spray-area-received-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        location_sprayed_percentage = getattr(
            settings, "LOCATION_SPRAYED_PERCENTAGE", 90
        )

        val = sum(
            1
            for l in self.get_descendants().filter(level="ta", target=True)
            if l.mda_received_percentage >= location_sprayed_percentage
        )
        cache.set(key, val)

        return val

    @cached_property
    def population_eligible(self):
        """Return the number of MDA population eligible."""
        key = "population-eligible-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        if self.level != "ta":
            val = sum(
                l.population_eligible
                for l in self.get_descendants().filter(level="ta", target=True)
            )
        else:
            queryset = (
                self.sprayday_set.filter(sprayable=True, was_sprayed=True)
                .annotate(
                    population=Cast(
                        KeyTextTransform("_population_eligible", "data"),
                        models.IntegerField(),
                    )
                )
                .aggregate(total_eligible=Sum("population"))
            )
            val = queryset["total_eligible"] or 0

        cache.set(key, val)

        return val

    @cached_property
    def population_treatment(self):
        """Return the number of MDA population treatment."""
        key = "population-treatment-{}".format(self.pk)
        val = cache.get(key)
        if val is not None:
            return val

        if self.level != "ta":
            val = sum(
                l.population_treatment
                for l in self.get_descendants().filter(level="ta", target=True)
            )
        else:
            queryset = (
                self.sprayday_set.filter(sprayable=True, was_sprayed=True)
                .annotate(
                    population=Cast(
                        KeyTextTransform("_population_treatment", "data"),
                        models.IntegerField(),
                    )
                )
                .aggregate(total_treatment=Sum("population"))
            )
            val = queryset["total_treatment"] or 0

        cache.set(key, val)

        return val
