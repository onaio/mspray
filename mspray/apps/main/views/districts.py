from django.db.models import Count
from rest_framework import viewsets


from mspray.apps.main.models import TargetArea
from mspray.apps.main.serializers.district import DistrictSerializer
from mspray.apps.main.serializers.target_area import TargetAreaSerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TargetArea.objects.filter(targeted=TargetArea.TARGETED_VALUE)\
        .values('district_name')\
        .annotate(num_target_areas=Count('district_name'))
    serializer_class = DistrictSerializer

    def get_serializer_class(self):
        district = self.request.QUERY_PARAMS.get('district')

        if district:
            return TargetAreaSerializer

        return super(DistrictViewSet, self).get_serializer_class()

    def filter_queryset(self, queryset):
        district = self.request.QUERY_PARAMS.get('district')

        if district:
            queryset = TargetArea.objects.filter(
                targeted=TargetArea.TARGETED_VALUE,
                district_name=district
            ).order_by('ranks', 'houses')

        return queryset
