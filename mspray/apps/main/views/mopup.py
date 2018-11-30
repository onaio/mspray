# -*- coding: utf-8 -*-
"""Mop-up view module.
"""
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.models.location import get_mopup_locations


def get_mopup_totals(
        district: object = None, queryset: object = None):
    """
    Get mopup totals for a queryset
    """
    if queryset is None:
        locations = district.get_locations_list_to_mopup()
    else:
        locations = queryset

    return {
        'structures_on_ground': sum(
            (_.structures_on_ground for _ in locations)),
        'visited_sprayed': sum((_.visited_sprayed for _ in locations)),
        'structures_to_mopup': sum((_.structures_to_mopup for _ in locations)),
        'mopup_days_needed': sum((_.mopup_days_needed for _ in locations)),
    }


class MopUpView(SiteNameMixin, ListView):
    """Mopup view.
    """

    context_object_name = "mopup_locations"
    template_name = "mop-up.html"
    queryset = Location.objects.filter(level="district", target=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = settings.MSPRAY_MOPUP_LABEL

        context['totals'] = {
            'health_centers_to_mopup':
            sum((_.health_centers_to_mopup
                 for _ in context[self.context_object_name])),
            'spray_areas_to_mopup':
            sum((_.spray_areas_to_mopup
                 for _ in context[self.context_object_name])),
            'structures_to_mopup':
            sum((_.structures_to_mopup
                 for _ in context[self.context_object_name])),
            'mopup_days_needed':
            sum((_.mopup_days_needed
                 for _ in context[self.context_object_name])),
        }

        # show definitions legend for mopup
        context.update(DEFINITIONS["mopup"][context.get("active_site", "IRS")])

        return context


class HealthFacilityMopUpView(SiteNameMixin, ListView):
    """Mopup view."""

    context_object_name = "mopup_locations"
    template_name = "health-facility-mop-up.html"
    queryset = Location.objects.filter(level="ta", target=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = settings.MSPRAY_MOPUP_LABEL
        context["district"] = get_object_or_404(
            Location, pk=self.kwargs["district"]
        )
        context[self.context_object_name] = get_mopup_locations(
            queryset=context[self.context_object_name])

        context['totals'] = get_mopup_totals(
            district=context["district"],
            queryset=context[self.context_object_name])

        # show definitions legend for mopup
        context.update(DEFINITIONS["mopup"][context.get("active_site", "IRS")])

        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(parent__parent_id=self.kwargs["district"])
        )
