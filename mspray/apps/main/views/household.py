from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from rest_framework import viewsets
from rest_framework import exceptions
from mspray.apps.main.models.household import Household
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.serializers.household import HouseholdSerializer


class HouseholdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer
    bbox_filter_field = 'geom'
    bbox_filter_include_overlapping = True  # Optional

    def filter_queryset(self, queryset):
        targetid = self.request.QUERY_PARAMS.get('target_area')

        if targetid:
            try:
                targetid = float(targetid)
            except ValueError:
                raise exceptions.ParseError(
                    _("Invalid targetid %s" % targetid))
            else:
                target = get_object_or_404(TargetArea, ranks=targetid)
                queryset = queryset.filter(geom__coveredby=target.geom)

        return queryset
