from rest_framework import viewsets

from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.serializers.target_area import TargetAreaSerializer


class TargetAreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TargetArea.objects.all()
    serializer_class = TargetAreaSerializer
