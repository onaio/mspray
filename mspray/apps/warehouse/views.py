from django.views.generic.detail import DetailView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.warehouse.druid import get_rhc_data


class LocationDetailView(SiteNameMixin, DetailView):
    template_name = 'warehouse/rhc.html'
    slug_field = 'pk'
    model = Location

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView, self).get_context_data(**kwargs)
        data = get_rhc_data(self.object.pk)
        context['data'] = data
        return context
