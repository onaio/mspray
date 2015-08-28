from dateutil.parser import parse
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import View

from mspray.apps.main.models import District
from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import TargetArea
from mspray.apps.main.serializers.target_area import TargetAreaSerializer
from mspray.apps.main.serializers.sprayday import SprayDaySerializer


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
        district_name = self.kwargs.get(self.slug_field)

        return qs.filter(district_name=district_name).order_by('targetid')

    def get_context_data(self, **kwargs):
        context = super(DistrictView, self).get_context_data(**kwargs)
        serializer = TargetAreaSerializer(context['object_list'], many=True,
                                          context={'request': self.request})
        context['district_list'] = serializer.data

        return context


class TargetAreaView(DetailView):
    template_name = 'madagascar/map.html'
    model = TargetArea
    slug_field = 'targetid'

    def get_context_data(self, **kwargs):
        context = super(TargetAreaView, self).get_context_data(**kwargs)
        serializer = TargetAreaSerializer(context['object'],
                                          context={'request': self.request})
        context['target_data'] = serializer.data

        spray_date = self.request.GET.get('spray_date')
        if spray_date:
            try:
                context['spray_date'] = parse(spray_date).date()
            except ValueError:
                pass

        context['target_areas'] = TargetArea.objects.filter(
            district_name=self.kwargs['district_name']
        ).values_list('targetid', flat=True)

        return context
