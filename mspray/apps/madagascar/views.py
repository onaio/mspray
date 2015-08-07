from django.shortcuts import render

from mspray.apps.main.models import District
from mspray.apps.main.serializers.target_area import TargetAreaSerializer


def index(request):
    qs = District.objects.filter().order_by('district_name')

    serializer = TargetAreaSerializer(qs, many=True,
                                      context={'request': request})
    context = {'district_list': serializer.data}

    return render(request, 'madagascar/index.html', context)
