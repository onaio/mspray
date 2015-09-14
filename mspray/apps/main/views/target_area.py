from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response

from mspray.apps.main.models import Location
from mspray.apps.main.models import Household
from mspray.apps.main.serializers.target_area import (
    TargetAreaSerializer, GeoTargetAreaSerializer)
from mspray.apps.main.serializers.household import HouseholdSerializer


class TargetAreaViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Location.objects.filter()
    serializer_class = TargetAreaSerializer

    def get_serializer_class(self):
        if self.format_kwarg == 'geojson':
            return GeoTargetAreaSerializer

        return super(TargetAreaViewSet, self).get_serializer_class()


class TargetAreaHouseholdsViewSet(mixins.RetrieveModelMixin,
                                  viewsets.GenericViewSet):
    queryset = Location.objects.filter()
    serializer_class = HouseholdSerializer

    def retrieve(self, request, **kwargs):
        data = []
        location = self.get_object()
        if location.geom is not None:
            households = Household.objects.filter(
                geom__coveredby=location.geom)
            serializer = self.get_serializer(households, many=True)
            data = serializer.data

        return Response(data)
