import json

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.serializers.sprayday import SprayDaySerializer


class SprayDayViewSet(viewsets.ModelViewSet):
    """
    List of households that have been sprayed.

    Query Parameters:
    - `day` - filter list of sprayed points for a specific day
    - `target_area` - filter spray points for a specific target
    - `ordering` - you can order by day field e.g `ordering=day` or \
    `ordering=-day`
    """
    queryset = SprayDay.objects.all()
    serializer_class = SprayDaySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('day',)
    ordering_fields = ('day',)
    ordering = ('day',)

    def filter_queryset(self, queryset):
        targetid = self.request.QUERY_PARAMS.get('target_area')

        if targetid:
            target = get_object_or_404(TargetArea, targetid=targetid,
                                       targeted=TargetArea.TARGETED_VALUE)
            queryset = queryset.filter(geom__contained=target.geom)

        return super(SprayDayViewSet, self).filter_queryset(queryset)

    def create(self, request, *args, **kwargs):
        has_id = request.DATA.get('_id')
        geolocation = request.DATA.get('_geolocation')

        if not has_id and not geolocation:
            data = {"error": _("Not a valid submission")}
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            geolocation = [float(p) for p in geolocation]
            point = json.dumps({'type': 'point', 'coordinates': geolocation})
            json_data = json.dumps(request.DATA)

            SprayDay.objects.create(day=1,
                                    data=json_data, geom=point)
            data = {"success": _("Successfully imported submission with"
                                 " submission id %(submission_id)s."
                                 % {'submission_id': has_id})}
            status_code = status.HTTP_201_CREATED

        return Response(data, status=status_code)
