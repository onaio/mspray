from rest_framework import viewsets
from rest_framework.response import Response

from mspray.apps.main.models import Way
from mspray.apps.main.serializers.osm import OsmSerializer
from mspray.libs.renderers import OSMRenderer


class OsmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Way.objects.all()
    serializer_class = OsmSerializer
    renderer_classes = (OSMRenderer,)

    def list(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)
