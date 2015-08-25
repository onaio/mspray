from django.shortcuts import render
from django.views.generic import View
from django.views.generic import ListView

from mspray.apps.main.models import District
from mspray.apps.main.models import TargetArea
from mspray.apps.main.serializers.target_area import TargetAreaSerializer


class IndexView(View):
    def get(self, request):
        qs = District.objects.filter().order_by('district_name')

        serializer = TargetAreaSerializer(qs, many=True,
                                          context={'request': request})
        context = {'district_list': serializer.data}

        return render(request, 'madagascar/index.html', context)


class DistrictView(ListView):
    template_name = 'madagascar/district.html'
    model = TargetArea
    slug_field = 'district_name'

    def get_queryset(self):
        qs = super(DistrictView, self).get_queryset()
        district_name = self.kwargs.get('slug')

        return qs.filter(district_name=district_name).order_by('targetid')

    def get_context_data(self, **kwargs):
        context = super(DistrictView, self).get_context_data(**kwargs)
        serializer = TargetAreaSerializer(context['object_list'], many=True,
                                          context={'request': self.request})
        context['district_list'] = serializer.data

        return context
