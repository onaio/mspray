from django.conf import settings
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response

from mspray.apps.main.models import Location
from mspray.apps.main.models import Household
from mspray.apps.main.models import SprayDay
from mspray.apps.main.serializers.target_area import (
    TargetAreaSerializer, GeoTargetAreaSerializer)
from mspray.apps.main.serializers.target_area import (
    NamibiaTargetAreaSerializer, GeoNamibiaTargetAreaSerializer)
from mspray.apps.main.serializers.household import HouseholdSerializer
from mspray.apps.main.serializers.household import HouseholdBSerializer
from mspray.apps.main.utils import get_ta_in_location


class TargetAreaViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Location.objects.filter()
    serializer_class = NamibiaTargetAreaSerializer

    def get_serializer_class(self):
        if self.format_kwarg == 'geojson':
            return GeoNamibiaTargetAreaSerializer

        return super(TargetAreaViewSet, self).get_serializer_class()


class TargetAreaHouseholdsViewSet(mixins.RetrieveModelMixin,
                                  viewsets.GenericViewSet):
    queryset = Location.objects.filter()
    serializer_class = HouseholdSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.kwargs.get('bgeom'):
            serializer_class = HouseholdBSerializer
        return serializer_class

    def retrieve(self, request, **kwargs):
        data = []
        location = self.get_object()
        if location.geom is not None:
            tas = list(get_ta_in_location(location))
            households = Household.objects.filter(location__in=tas)

            if settings.OSM_SUBMISSIONS:
                spray_points = SprayDay.objects.exclude(geom=None)\
                    .filter(location__in=tas).values('geom')
                exclude = households.filter(geom__in=spray_points)\
                    .values_list('pk', flat=True)
                households = households.exclude(pk__in=exclude)

            serializer = self.get_serializer(households, many=True)
            data = serializer.data

        return Response(data)
