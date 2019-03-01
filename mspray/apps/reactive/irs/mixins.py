"""mixins module for Reactive IRS"""
from collections import Counter

from django.conf import settings
from mspray.apps.main.utils import parse_spray_date
from mspray.apps.main.models import Household, Location, SprayDay
from mspray.apps.main.serializers.target_area import count_duplicates
from mspray.apps.reactive.irs.queries import get_spray_data_using_geoquery

CHW_LEVEL = getattr(settings, "MSPRAY_REACTIVE_IRS_CHW_LOCATION_LEVEL", "chw")


class CHWLocationMixin:
    """Mixin for CHW location serializers"""

    def get_sprayday_qs(self, obj):
        """Get queryset for spray days"""
        return SprayDay.objects.filter(geom__coveredby=obj.geom)

    def get_structures_in_location(self, obj):
        """Get location structures"""
        return Household.objects.filter(geom__coveredby=obj.geom).count()

    def get_spray_data(self, obj):
        """Get spray data"""
        context = self.context
        return get_spray_data_using_geoquery(location=obj, context=context)

    def get_duplicates(self, obj, was_sprayed=True):
        """Get duplicates"""
        spray_date = None
        request = self.context.get("request")
        if request:
            spray_date = parse_spray_date(request)
        qs = self.get_sprayday_qs(obj)
        return count_duplicates(
            obj=obj,
            was_sprayed=was_sprayed,
            spray_date=spray_date,
            sprayday_qs=qs)

    def get_num_new_structures(self, obj):
        """Get num_new_structures"""
        data = self.get_spray_data(obj)
        return data.get("new_structures") or 0

    def get_found(self, obj):
        """Get found"""
        data = self.get_spray_data(obj)
        return data.get("found") or 0

    def get_visited_total(self, obj):
        """Get visited_total"""
        return self.get_visited_sprayed(obj)

    def get_visited_sprayed(self, obj):
        """Get visited_sprayed"""
        data = self.get_spray_data(obj)
        return data.get("sprayed") or 0

    def get_visited_not_sprayed(self, obj):
        """Get visited_not_sprayed"""
        data = self.get_spray_data(obj)
        return data.get("not_sprayed") or 0

    def get_visited_refused(self, obj):
        """Get visited_refused"""
        data = self.get_spray_data(obj)
        return data.get("refused") or 0

    def get_visited_other(self, obj):
        data = self.get_spray_data(obj)
        return data.get("other") or 0

    def get_not_visited(self, obj):
        """Get not_visited"""
        data = self.get_spray_data(obj)
        structures = self.get_structures_in_location(obj)
        duplicates = self.get_duplicates(obj=obj, was_sprayed=True)

        not_sprayable = data.get("not_sprayable") or 0
        new_structures = data.get("new_structures") or 0
        structures = structures - not_sprayable
        structures = structures + new_structures + duplicates
        count = data.get("found") or 0

        return structures - count

    def get_structures(self, obj):
        """Get structures"""
        data = self.get_spray_data(obj)
        structures = self.get_structures_in_location(obj)
        duplicates = self.get_duplicates(obj=obj, was_sprayed=True)
        not_sprayable = data.get("not_sprayable") or 0
        new_structures = data.get("new_structures") or 0
        structures = structures - not_sprayable
        structures = structures + new_structures + duplicates
        return structures

    def get_total_structures(self, obj):
        """Get total_structures"""
        return self.get_structures(obj)

    def get_spray_dates(self, obj):
        """ Get spray dates """
        queryset = self.get_sprayday_qs(obj)

        return (queryset.values_list(
            "spray_date", flat=True).order_by("spray_date").distinct())

    def get_bounds(self, obj):
        """Get bounds"""
        bounds = []
        if obj:
            if isinstance(obj, dict):
                bounds = [
                    obj.get("xmin"),
                    obj.get("ymin"),
                    obj.get("xmax"),
                    obj.get("ymax"),
                ]
            elif obj.geom:
                bounds = list(obj.geom.boundary.extent)

        return bounds

    def get_district_name(self, obj):
        """Get district_name"""
        return obj.name


class CHWinLocationMixin(CHWLocationMixin):
    """
    Mixin meant to be used in serializers for locations that are not CHWs
    """

    def get_spray_data(self, obj):
        """Get spray data"""
        result = Counter()
        chw_objects = Location.objects.filter(parent=obj, level=CHW_LEVEL)
        for chw_obj in chw_objects:
            spray_data = get_spray_data_using_geoquery(location=chw_obj)
            result.update(spray_data)

        return result
