import operator

from django.views.generic.detail import DetailView
from django.views.generic import TemplateView

from rest_framework.renderers import JSONRenderer

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.warehouse.druid import get_druid_data, process_location_data,\
    calculate_target_area_totals
from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.warehouse.serializers import TargetAreaSerializer
from mspray.apps.warehouse.utils import get_duplicates


class Home(SiteNameMixin, TemplateView):
    template_name = 'warehouse/home.html'

    def get_queryset(self):
        return Location.objects.filter(level='district', parent=None).values(
            'id', 'name', 'structures')

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context.update(DEFINITIONS['district'])
        data, totals = get_druid_data(dimensions=[
            'target_area_id', 'target_area_name', 'target_area_structures',
            'rhc_name', 'district_name', 'district_id']
        )
        object_list = Location.objects.filter(
            level='district', parent=None).values(
            'id', 'name', 'structures', 'level')
        for district in object_list:
            district_data = [x for x in data if x['district_id'] ==
                             str(district['id'])]
            result = process_location_data(district, district_data)
            district.update(result)
        context['object_list'] = object_list
        return context


class DistrictView(SiteNameMixin, DetailView):
    template_name = 'warehouse/district.html'
    slug_field = 'pk'
    model = Location

    def get_queryset(self):
        return Location.objects.filter(level='district')

    def get_context_data(self, **kwargs):
        context = super(DistrictView, self).get_context_data(**kwargs)
        context.update(DEFINITIONS['RHC'])
        data, totals = get_druid_data(dimensions=[
            'target_area_id', 'target_area_name', 'target_area_structures',
            'rhc_name', 'district_name', 'rhc_id']
        )
        object_list = Location.objects.filter(
            level='RHC', parent=self.object).values(
            'id', 'name', 'structures', 'level')
        for rhc in object_list:
            rhc_data = [x for x in data if x['rhc_id'] == str(rhc['id'])]
            result = process_location_data(rhc, rhc_data)
            rhc.update(result)
        context['object_list'] = object_list
        return context


class RHCView(SiteNameMixin, DetailView):
    template_name = 'warehouse/rhc.html'
    slug_field = 'pk'
    model = Location

    def get_queryset(self):
        return Location.objects.filter(level='RHC')

    def get_context_data(self, **kwargs):
        context = super(RHCView, self).get_context_data(**kwargs)
        data, totals = get_druid_data(filter_list=[['rhc_id',
                                                    operator.eq,
                                                    self.object.pk]])
        context['data'] = data
        context.update(DEFINITIONS['ta'])
        # update data with numbers of any missing target areas
        ids_present = []
        for x in data:
            try:
                ids_present.append(int(x['target_area_id']))
            except TypeError:
                pass
        missing = self.object.get_children().exclude(
            id__in=ids_present).values('name', 'structures')
        if missing:
            for m in missing:
                totals['structures'] += m['structures']
            context['missing_target_areas'] = missing
        context['totals'] = calculate_target_area_totals(totals)
        return context


class TargetAreaMap(SiteNameMixin, DetailView):
    template_name = 'warehouse/maps/target_area.html'
    slug_field = 'pk'
    model = Location

    def get_queryset(self):
        return Location.objects.filter(level='ta')

    def get_context_data(self, **kwargs):
        context = super(TargetAreaMap, self).get_context_data(**kwargs)
        data, totals = get_druid_data(
            filter_list=[['target_area_id', operator.eq, self.object.pk]],
            dimensions=['target_area_id', 'target_area_name',
                        'target_area_structures', 'district_name',
                        'district_id', 'rhc_name', 'rhc_id']
        )
        ta_data = TargetAreaSerializer(self.object, druid_data=data[0]).data
        sprayed_duplicates = get_duplicates(ta_pk=self.object.id, sprayed=True)
        not_sprayed_duplicates = get_duplicates(ta_pk=self.object.id,
                                                sprayed=False)
        context['sprayed_duplicates'] = len(sprayed_duplicates)
        context['sprayed_duplicates_data'] = sprayed_duplicates
        context['not_sprayed_duplicates'] = len(not_sprayed_duplicates)
        context['not_sprayed_duplicates_data'] = not_sprayed_duplicates
        context['target_data'] = JSONRenderer().render(ta_data)
        return context


class RHCMap(SiteNameMixin, DetailView):
    template_name = 'warehouse/maps/rhc.html'
    slug_field = 'pk'
    model = Location

    def get_queryset(self):
        return Location.objects.filter(level='RHC')

    def get_context_data(self, **kwargs):
        context = super(RHCMap, self).get_context_data(**kwargs)
        data, totals = get_druid_data(filter_list=[['rhc_id', operator.eq,
                                      self.object.pk]])
        ta_data = TargetAreaSerializer(self.object, druid_data=data[0]).data
        context['target_data'] = JSONRenderer().render(ta_data)
        return context


class AllTargetAreas(SiteNameMixin, TemplateView):
    template_name = 'warehouse/spray-areas.html'

    def get_context_data(self, **kwargs):
        context = super(AllTargetAreas, self).get_context_data(**kwargs)
        data, totals = get_druid_data(dimensions=[
            'target_area_id', 'target_area_name', 'target_area_structures',
            'rhc_name', 'district_name']
        )
        context['data'] = data
        context.update(DEFINITIONS['ta'])
        # update data with numbers of any missing target areas
        ids_present = []
        for x in data:
            try:
                ids_present.append(int(x['target_area_id']))
            except TypeError:
                pass
        missing = Location.objects.select_related(
            'parent').filter(level='ta').exclude(id__in=ids_present).values(
            'name', 'parent__name', 'parent__parent__name', 'structures')
        if missing:
            for m in missing:
                totals['structures'] += m['structures']
            context['missing_target_areas'] = missing
        context['totals'] = calculate_target_area_totals(totals)
        return context
