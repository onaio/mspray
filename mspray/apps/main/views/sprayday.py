import json

from django.utils.translation import ugettext as _
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.serializers.sprayday import SprayDaySerializer


class SprayDayViewSet(viewsets.ModelViewSet):
    queryset = SprayDay.objects.all()
    serializer_class = SprayDaySerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('day',)

    def create(self, request, *args, **kwargs):
        has_id = request.DATA.get('_id')
        geolocation = request.DATA.get('_geolocation')

        if not has_id and not geolocation:
            data = {"error": _(u"Not a valid submission")}
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            geolocation = [float(p) for p in geolocation]
            point = json.dumps({'type': 'point', 'coordinates': geolocation})
            json_data = json.dumps(request.DATA)

            SprayDay.objects.create(day=1,
                                    data=json_data, geom=point)
            data = {"success": _(u"Successfully imported submission with"
                                 " submission id %(submission_id)s."
                                 % {'submission_id': has_id})}
            status_code = status.HTTP_201_CREATED

        return Response(data, status=status_code)
