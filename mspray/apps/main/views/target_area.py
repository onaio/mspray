from django.shortcuts import get_list_or_404
from rest_framework import viewsets

from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.serializers.target_area import TargetAreaSerializer


class TargetAreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TargetArea.objects.all()
    serializer_class = TargetAreaSerializer

    def filter_queryset(self, queryset):
        targetid = self.request.QUERY_PARAMS.get('target_area')

        if targetid:
            queryset = get_list_or_404(TargetArea, targetid=targetid)

        return super(TargetAreaViewSet, self).filter_queryset(queryset)
