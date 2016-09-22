from rest_framework import viewsets
from rest_framework.response import Response

from mspray.apps.main.models import Way, Location
from mspray.apps.main.serializers.osm import OsmSerializer
from mspray.libs.renderers import OSMRenderer


class OsmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Way.objects.all()
    serializer_class = OsmSerializer
    renderer_classes = (OSMRenderer,)

    def list(self, request, *args, **kwargs):
        code = request.query_params.get('code')
        location = code and Location.objects.filter(code=code).first()
        qs = self.get_queryset()
        if code and location:
            self.object_list = qs.filter(geom__contained=location.geom)
        elif code and location is None:
            self.object_list = qs.none()
        else:
            self.object_list = qs

        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)
