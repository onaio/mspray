from django.shortcuts import render
from django.views.generic import View
from django.views.generic import DetailView

from mspray.apps.main.models import District
from mspray.apps.main.models import TargetArea
from mspray.apps.main.serializers.target_area import TargetAreaByDataSerializer


class IndexView(View):
    def get(self, request):
        qs = District.objects.filter().order_by('district_name')

        serializer = TargetAreaByDataSerializer(
            qs, many=True, context={'request': request}
        )
        context = {'district_list': serializer.data}

        return render(request, 'madagascar/index.html', context)


class DistrictView(DetailView):
    template_name = 'madagascar/district.html'
    model = District
    slug_field = 'pk'

    def get_context_data(self, **kwargs):
        context = super(DistrictView, self).get_context_data(**kwargs)
        qs = TargetArea.objects.filter(
            district=context['object']
        )
        serializer = TargetAreaByDataSerializer(
            qs, many=True, context={'request': self.request}
        )
        context['district_list'] = serializer.data

        return context
