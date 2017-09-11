from django.views.generic.detail import DetailView
from django.views.generic import TemplateView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.warehouse.druid import get_rhc_data, calculate_rhc_totals
from mspray.apps.main.definitions import DEFINITIONS


class LocationDetailView(SiteNameMixin, DetailView):
    template_name = 'warehouse/rhc.html'
    slug_field = 'pk'
    model = Location

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView, self).get_context_data(**kwargs)
        data, totals = get_rhc_data(self.object.pk)
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
        context['totals'] = calculate_rhc_totals(totals)
        return context


class TargetAreas(SiteNameMixin, TemplateView):
    template_name = 'warehouse/spray-areas.html'

    def get_context_data(self, **kwargs):
        context = super(TargetAreas, self).get_context_data(**kwargs)
        data, totals = get_rhc_data(pk=None, dimensions=[
                                    'target_area_id',
                                    'target_area_name',
                                    'target_area_structures',
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
        # missing = [y for y in target_areas if y.id not in ids_present]
        missing = Location.objects.select_related(
            'parent').filter(level='ta').exclude(id__in=ids_present).values(
            'name', 'parent__name', 'parent__parent__name', 'structures')
        if missing:
            for m in missing:
                totals['structures'] += m['structures']
            context['missing_target_areas'] = missing
        context['totals'] = calculate_rhc_totals(totals)
        return context
