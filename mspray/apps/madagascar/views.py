from dateutil.parser import parse
from django.views.generic import DetailView
from django.views.generic import ListView

from mspray.apps.main.models import District
from mspray.apps.main.models import TargetArea
from mspray.apps.main.serializers.target_area import TargetAreaSerializer


class DistrictView(ListView):
    template_name = 'madagascar/district.html'
    model = District
    slug_field = 'district_name'

    def get_queryset(self):
        district_name = self.kwargs.get(self.slug_field)
        if district_name is not None:
            qs = TargetArea.objects.filter(district_name=district_name)\
                .order_by('targetid')
        else:
            qs = super(DistrictView, self).get_queryset()\
                .order_by('district_name')

        return qs

    def get_context_data(self, **kwargs):
        context = super(DistrictView, self).get_context_data(**kwargs)
        serializer = TargetAreaSerializer(context['object_list'], many=True,
                                          context={'request': self.request})
        context['district_list'] = serializer.data
        fields = ['structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited']
        totals = {}
        for rec in serializer.data:
            for field in fields:
                totals[field] = rec[field] + (totals[field]
                                              if field in totals else 0)
        context['district_name'] = self.kwargs.get(self.slug_field)
        context['districts'] = District.objects\
            .values_list('district_name', flat=True).order_by('district_name')
        context['district_totals'] = totals

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

        context['districts'] = District.objects\
            .values_list('district_name', flat=True).order_by('district_name')

        context['district_name'] = self.kwargs.get('district_name')

        return context
