from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from mspray.apps.main.models.household import Household
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.serializers.household import HouseholdSerializer


class HouseholdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer
    bbox_filter_field = 'geom'
    bbox_filter_include_overlapping = True  # Optional

    def filter_queryset(self, queryset):
        targetid = self.request.QUERY_PARAMS.get('target_area')

        if targetid:
            target = get_object_or_404(TargetArea, targetid=targetid,
                                       targeted=TargetArea.TARGETED_VALUE)
            queryset = queryset.filter(geom__coveredby=target.geom)

        return queryset
