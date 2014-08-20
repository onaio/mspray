from django.shortcuts import get_list_or_404
from rest_framework import viewsets

from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.serializers.target_area import (
    TargetAreaSerializer, GeoTargetAreaSerializer)


class TargetAreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TargetArea.objects.filter(targeted=TargetArea.TARGETED_VALUE)
    serializer_class = TargetAreaSerializer

    def get_serializer_class(self):
        if self.format_kwarg == 'geojson':
            return GeoTargetAreaSerializer

        return super(TargetAreaViewSet, self).get_serializer_class()

    def filter_queryset(self, queryset):
        targetid = self.request.QUERY_PARAMS.get('target_area')

        if targetid:
            queryset = get_list_or_404(TargetArea, rank_house=targetid,
                                       targeted=TargetArea.TARGETED_VALUE)

        return super(TargetAreaViewSet, self).filter_queryset(queryset)
