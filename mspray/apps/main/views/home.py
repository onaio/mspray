from dateutil.parser import parse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.models import TargetArea
from mspray.apps.main.serializers.target_area import TargetAreaSerializer
from mspray.apps.main.views.target_area import TargetAreaViewSet
from mspray.apps.main.views.target_area import TargetAreaHouseholdsViewSet


class DistrictView(SiteNameMixin, ListView):
    template_name = 'home/district.html'
    model = Location
    slug_field = 'district_name'

    def get_queryset(self):
        qs = super(DistrictView, self).get_queryset()
        district_name = self.kwargs.get(self.slug_field)
        if district_name is not None:
            qs = qs.filter(parent__code=district_name)
        else:
            qs = super(DistrictView, self).get_queryset()\
                .filter(parent=None).order_by('name')

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
        district_code = self.kwargs.get(self.slug_field)
        if district_code:
            district = get_object_or_404(
                Location, code=district_code
            )
            context['district'] = district
            context['district_code'] = district.code
            context['district_name'] = district.name
        context['districts'] = Location.objects.filter(parent=None)\
            .values_list('code', 'name').order_by('name')
        context['district_totals'] = totals
        context['ta_level'] = settings.MSPRAY_TA_LEVEL

        return context


class TargetAreaView(SiteNameMixin, DetailView):
    template_name = 'home/map.html'
    model = Location
    slug_field = 'code'

    def get_context_data(self, **kwargs):
        context = super(TargetAreaView, self).get_context_data(**kwargs)
        serializer = TargetAreaSerializer(context['object'],
                                          context={'request': self.request})
        context['target_data'] = serializer.data
        view = TargetAreaViewSet.as_view({'get': 'retrieve'})
        response = view(self.request, pk=context['object'].pk,
                        format='geojson')
        response.render()
        context['ta_geojson'] = response.content

        hhview = TargetAreaHouseholdsViewSet.as_view({'get': 'retrieve'})
        response = hhview(self.request, pk=context['object'].pk,
                          format='geojson')
        response.render()
        context['hh_geojson'] = response.content

        spray_date = self.request.GET.get('spray_date')
        if spray_date:
            try:
                context['spray_date'] = parse(spray_date).date()
            except ValueError:
                pass

        context['target_areas'] = TargetArea.objects.filter(
            district_name=self.kwargs['district_name']
        ).values_list('targetid', flat=True)

        context['districts'] = Location.objects.filter(parent=None)\
            .values_list('code', 'name').order_by('name')

        district_code = self.kwargs.get('district_name')
        if district_code:
            context['district_code'] = district_code
            context['district_name'] = get_object_or_404(
                Location, code=district_code
            ).name

        return context
