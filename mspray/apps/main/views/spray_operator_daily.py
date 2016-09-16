from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework import status

from mspray.apps.main.models import SprayOperatorDailySummary
from mspray.apps.main.serializers.sprayday import SprayOperatorDailySerializer
from mspray.apps.main.utils import add_spray_operator_daily


class SprayOperatorDailyViewSet(viewsets.ModelViewSet):
    queryset = SprayOperatorDailySummary.objects.all()
    serializer_class = SprayOperatorDailySerializer

    def create(self, request, *args, **kwargs):
        try:
            add_spray_operator_daily(request.data)
        except Exception as e:
            raise ParseError(e)

        return Response("Successfully created", status=status.HTTP_201_CREATED)
