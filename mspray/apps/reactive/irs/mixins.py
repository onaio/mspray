"""mixins module for Reactive IRS"""
from mspray.apps.main.models import Household, SprayDay


class CHWLocationMixin:
    """Mixin for CHW location serializers"""

    def get_sprayday_qs(self, obj):
        """Get queryset for spray days"""
        return SprayDay.objects.filter(geom__coveredby=obj.geom)

    def get_structures(self, obj):
        """Get structures"""
        return Household.objects.filter(geom__coveredby=obj.geom).count()

    def get_total_structures(self, obj):
        """Get total_structures"""
        return self.get_structures(obj) + self.get_not_visited(obj)

    def get_num_new_structures(self, obj):
        """Get num_new_structures"""
        return 0

    def get_found(self, obj):
        """Get found"""
        return self.get_visited_sprayed(obj)

    def get_visited_total(self, obj):
        """Get visited_total"""
        return self.get_visited_sprayed(obj)

    def get_visited_sprayed(self, obj):
        """Get visited_sprayed"""
        qs = self.get_sprayday_qs(obj)
        return qs.filter(was_sprayed=True, sprayable=True).count()

    def get_visited_not_sprayed(self, obj):
        """Get visited_not_sprayed"""
        qs = self.get_sprayday_qs(obj)
        return qs.filter(was_sprayed=False, sprayable=True).count()

    def get_visited_refused(self, obj):
        """Get visited_refused"""
        qs = self.get_sprayday_qs(obj)
        return qs.filter(was_sprayed=False, sprayable=True).count()

    def get_visited_other(self, obj):
        """Get visited_other"""
        return 0

    def get_not_visited(self, obj):
        """Get not_visited"""
        qs = self.get_sprayday_qs(obj)
        return qs.filter(sprayable=False).count()

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
