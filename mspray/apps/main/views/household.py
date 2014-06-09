import json

from django.contrib.gis.geos import MultiPolygon

from rest_framework import viewsets
from rest_framework.response import Response

from mspray.apps.main.models.household import Household
from mspray.apps.main.serializers.household import (
    HouseholdSerializer, BufferHouseholdSerializer)


class HouseholdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer

    def filter_queryset(self, queryset):
        distance = 0.00039

        buffered = self.request.QUERY_PARAMS.get('buffer')

        if buffered == "true":
            self.serializer_class = BufferHouseholdSerializer
            for hh in queryset:
                hh.bgeom = hh.geom.buffer(distance)

        return queryset

    def list(self, request, *args, **kwargs):
        buffered = request.QUERY_PARAMS.get('buffer')

        if buffered == "true":
            self.object_list = self.filter_queryset(self.get_queryset())
            bf = MultiPolygon([item.bgeom for item in self.object_list])
            data = [
                json.loads(p.geojson) for p in bf.cascaded_union.simplify()]

            return Response(data=data)

        return super(HouseholdViewSet, self).list(request, *args, **kwargs)
