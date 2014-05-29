from rest_framework import viewsets

from mspray.apps.main.models.household import Household
from mspray.apps.main.serializers.household import HouseholdSerializer


class HouseholdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer
