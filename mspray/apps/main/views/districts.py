from django.db.models import Count
from rest_framework import viewsets


from mspray.apps.main.models import TargetArea
from mspray.apps.main.serializers.district import DistrictSerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TargetArea.objects.values('district_name')\
        .annotate(num_target_areas=Count('district_name'))
    serializer_class = DistrictSerializer
