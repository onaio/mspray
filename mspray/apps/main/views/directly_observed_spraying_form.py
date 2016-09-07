from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError

from mspray.apps.main.models import DirectlyObservedSprayingForm
from mspray.apps.main.serializers.sprayday import (
    DirectlyObservedSprayingFormSerializer
)


class DirectlyObservedSprayingFormViewSet(viewsets.ModelViewSet):
    queryset = DirectlyObservedSprayingForm.objects.all()
    serializer_class = DirectlyObservedSprayingFormSerializer

    def create(self, request, *args, **kwargs):
        try:
            DirectlyObservedSprayingForm.objects.create(
                correct_removal=request.data.get('correct_removal'),
                correct_mix=request.data.get('correct_mix'),
                rinse=request.data.get('rinse'),
                PPE=request.data.get('PPE'),
                CFV=request.data.get('CFV'),
                correct_covering=request.data.get('correct_covering'),
                leak_free=request.data.get('leak_free'),
                correct_distance=request.data.get('correct_distance'),
                correct_speed=request.data.get('correct_speed'),
                correct_overlap=request.data.get('correct_overlap'),
                district=request.data.get('district'),
                health_facility=request.data.get('health_facility'),
                supervisor_name=request.data.get('supervisor_name'),
                sprayop_code_name=request.data.get('sprayop_code_name'),
                tl_code_name=request.data.get('tl_code_name'),
                data=request.data,
                spray_date=request.data.get('today'),
            )
        except Exception as e:
            raise ParseError(e)

        return Response("Successfully created", status=status.HTTP_201_CREATED)
