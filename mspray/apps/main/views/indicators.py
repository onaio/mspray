from django.shortcuts import get_object_or_404

from rest_framework import views
from rest_framework.response import Response

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.serializers.household import HouseholdSerializer


class Indicator(object):
    value = None

    def get_value(self):
        if self.value is None:
            self.calculate()

        return self.value

    def _set_value(self, value):
        self.value = value

    def calculate(self):
        raise NotImplemented("calculate method has not been implemented")


class NumberOfHouseholdsInTargetArea(Indicator):
    geom = None

    def __init__(self, geom):
        self.geom = geom

    def calculate(self):
        count = Household.objects.filter(geom__within=self.geom).count()
        self._set_value(count)


class NumberOfHouseholdsIndicatorView(views.APIView):
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer

    def get_indicator(self, target_area):
        return {
            'number_of_households':
            NumberOfHouseholdsInTargetArea(target_area.geom).get_value(),
            'target_area': target_area.name
        }

    def get(self, request, *args, **kwargs):
        pk_target = request.QUERY_PARAMS.get('target', None)
        data = []

        if pk_target:
            ta = get_object_or_404(TargetArea, pk=pk_target)
            data = self.get_indicator(ta)
        else:
            for ta in TargetArea.objects.all():
                data.append(self.get_indicator(ta))

        return Response(data)
