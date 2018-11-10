# -*- coding: utf-8 -*-
"""Update structure counts in locations command."""
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location, Household


class Command(BaseCommand):
    """Update structure counts in locations."""

    help = _(
        "Update location structure numbers for districts/regions"
        " from target areas"
    )

    def handle(self, *args, **options):
        def _update_location_structures(level):
            locations = Location.objects.filter(level=level, target=True)
            for loc in locations.iterator():
                structures = loc.location_set.aggregate(
                    structure_sum=Sum("structures")
                )["structure_sum"]
                if structures:
                    loc.structures = structures
                    loc.save()

        def _update_spray_areas_structures():
            for loc in Location.objects.filter(level="ta"):
                num_structures = Household.objects.filter(location=loc).count()
                loc.structures = num_structures
                loc.save()

        def _update_num_of_spray_areas():
            for loc in Location.objects.filter(level="RHC"):
                num_ta = (
                    loc.get_children().filter(level="ta", target=True).count()
                )
                loc.num_of_spray_areas = num_ta
                loc.save()

                district = loc.parent
                if district:
                    district_num_ta = (
                        district.get_descendants()
                        .filter(level="ta", target=True)
                        .count()
                    )
                    district.num_of_spray_areas = district_num_ta
                    district.save()

        _update_spray_areas_structures()
        for level in ["RHC", "district"]:
            _update_location_structures(level)

        _update_num_of_spray_areas()
