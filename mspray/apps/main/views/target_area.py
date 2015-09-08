from rest_framework import viewsets
from rest_framework import mixins

from mspray.apps.main.models import Location
from mspray.apps.main.serializers.target_area import (
    TargetAreaSerializer, GeoTargetAreaSerializer)


class TargetAreaViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Location.objects.filter()
    serializer_class = TargetAreaSerializer

    def get_serializer_class(self):
        if self.format_kwarg == 'geojson':
            return GeoTargetAreaSerializer

        return super(TargetAreaViewSet, self).get_serializer_class()
