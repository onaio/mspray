import json

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from django.contrib.gis.geos import MultiPolygon

from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework.response import Response

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.serializers.household import (
    HouseholdSerializer, BufferHouseholdSerializer)


class HouseholdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer
    bbox_filter_field = 'geom'
    bbox_filter_include_overlapping = True  # Optional

    def filter_queryset(self, queryset):
        distance = 0.00009

        buffered = self.request.QUERY_PARAMS.get('buffer')
        targetid = self.request.QUERY_PARAMS.get('target_area')

        if targetid:
            try:
                targetid = float(targetid)
            except ValueError:
                raise exceptions.ParseError(
                    _("Invalid targetid %s" % targetid))
            else:
                target = get_object_or_404(TargetArea, targetid=targetid)
                queryset = queryset.filter(geom__coveredby=target.geom)

        if buffered == "true":
            self.serializer_class = BufferHouseholdSerializer
            for hh in queryset:
                hh.bgeom = hh.geom.buffer(distance)
        else:
            return super(HouseholdViewSet, self).filter_queryset(queryset)

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
