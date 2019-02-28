"""mixins module for Reactive IRS"""
from mspray.apps.main.models import Household, SprayDay
from mspray.apps.main.serializers.target_area import count_duplicates
from mspray.apps.reactive.irs.queries import get_spray_data_using_geoquery


class CHWLocationMixin:
    """Mixin for CHW location serializers"""

    def get_sprayday_qs(self, obj):
        """Get queryset for spray days"""
        return SprayDay.objects.filter(geom__coveredby=obj.geom)

    def get_structures_in_location(self, obj):
        """Get location structures"""
        return Household.objects.filter(geom__coveredby=obj.geom).count()

    def get_duplicates(self, obj, was_sprayed=True):
        """Get duplicates"""
        qs = self.get_sprayday_qs(obj)
        return count_duplicates(
            obj=obj, was_sprayed=was_sprayed, sprayday_qs=qs)

    def get_spray_data(self, obj):
        """Get spray data"""
        return get_spray_data_using_geoquery(location=obj)

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
        return data.get("sprayed")

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

    def get_district_name(self, obj):
        """Get district_name"""
        return obj.code

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
