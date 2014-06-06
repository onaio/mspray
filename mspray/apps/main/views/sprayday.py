from rest_framework import filters
from rest_framework import viewsets

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.serializers.sprayday import SprayDaySerializer


class SprayDayViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SprayDay.objects.all()
    serializer_class = SprayDaySerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('day',)