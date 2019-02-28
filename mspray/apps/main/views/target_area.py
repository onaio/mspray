from django.conf import settings

from rest_framework import mixins, viewsets
from rest_framework.response import Response

from mspray.apps.main.models import Household, Location, SprayDay
from mspray.apps.main.query import get_location_qs
from mspray.apps.main.serializers.household import (HouseholdBSerializer,
                                                    HouseholdSerializer)
from mspray.apps.main.serializers.target_area import (GeoTargetAreaSerializer,
                                                      TargetAreaSerializer)
from mspray.apps.main.utils import get_ta_in_location


class TargetAreaViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = get_location_qs(Location.objects.filter())
    serializer_class = TargetAreaSerializer

    def get_serializer_class(self):
        if self.format_kwarg == "geojson":
            return GeoTargetAreaSerializer

        return super(TargetAreaViewSet, self).get_serializer_class()


class HouseholdsViewSetMixin:
    """HouseholdsViewSet mixin"""

    queryset = get_location_qs(Location.objects.filter())
    serializer_class = HouseholdSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.kwargs.get("bgeom"):
            serializer_class = HouseholdBSerializer
        return serializer_class


class TargetAreaHouseholdsViewSet(HouseholdsViewSetMixin,
                                  mixins.RetrieveModelMixin,
                                  viewsets.GenericViewSet):
    def retrieve(self, request, **kwargs):  # pylint: disable=arguments-differ
        data = []
        location = self.get_object()
        if location.geom is not None:
            tas = list(get_ta_in_location(location))
            households = Household.objects.filter(location__in=tas)

            if settings.OSM_SUBMISSIONS:
                spray_points = SprayDay.objects.exclude(geom=None)
                spray_date = self.kwargs.get("spray_date")
                if spray_date:
                    spray_points = spray_points.filter(
                        spray_date__lte=spray_date)
                spray_points = spray_points.filter(
                    location__in=tas).values("geom")
                exclude = households.filter(
                    hh_id__in=spray_points.values("osmid")).values_list(
                        "pk", flat=True)
                households = households.exclude(pk__in=exclude)

            serializer = self.get_serializer(households, many=True)
            data = serializer.data

        return Response(data)


class CHWHouseholdsViewSet(HouseholdsViewSetMixin, mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    def retrieve(self, request, **kwargs):  # pylint: disable=arguments-differ
        data = []
        location = self.get_object()
        if location.geom is not None:
            households = Household.objects.filter(
                geom__coveredby=location.geom)

            if settings.OSM_SUBMISSIONS:
                spray_points = SprayDay.objects.exclude(geom=None)
                spray_date = self.kwargs.get("spray_date")
                if spray_date:
                    spray_points = spray_points.filter(
                        spray_date__lte=spray_date)
                spray_points = spray_points.filter(
                    geom__coveredby=location.geom).values("geom")
                exclude = households.filter(
                    hh_id__in=spray_points.values("osmid")).values_list(
                        "pk", flat=True)
                households = households.exclude(pk__in=exclude)

            serializer = self.get_serializer(households, many=True)
            data = serializer.data

        return Response(data)
