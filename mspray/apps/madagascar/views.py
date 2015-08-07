from django.shortcuts import render
from django.views.generic import View

from mspray.apps.main.models import District
from mspray.apps.main.serializers.target_area import TargetAreaSerializer


class IndexView(View):
    def get(self, request):
        qs = District.objects.filter().order_by('district_name')

        serializer = TargetAreaSerializer(qs, many=True,
                                          context={'request': request})
        context = {'district_list': serializer.data}

        return render(request, 'madagascar/index.html', context)
