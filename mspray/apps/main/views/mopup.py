# -*- coding: utf-8 -*-
"""Mop-up view module.
"""
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location


def get_mopup_locations(queryset):
    """
    Returns locations for mop-up
    """
    lower_bound = getattr(settings, 'MSPRAY_MOPUP_LOWER_BOUND', 0.2)
    return [
        location for location in queryset.iterator()
        if location.structures_to_mopup > 0 and
        location.structures_on_ground > 0 and
        (location.visited_found / location.structures_on_ground) > lower_bound
    ]


def get_district_mopup_totals(district_id, queryset=None):
    """
    Get mopup data for a district
    """
    if queryset is None:
        target_areas = Location.objects.filter(
            level="ta",
            target=True).filter(parent__parent_id=district_id)

        locations = get_mopup_locations(queryset=target_areas)
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

        context['totals'] = get_district_mopup_totals(
            district_id=self.kwargs["district"],
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
