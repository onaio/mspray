# -*- coding: utf-8 -*-
"""Mop-up view module.
"""
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.models import Location


class MopUpView(ListView):
    """Mopup view.
    """

    context_object_name = "mopup_locations"
    template_name = "mop-up.html"
    queryset = Location.objects.filter(level="district", target=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["site_name"] = "Mop-up"

        # show definitions legend for mopup
        context.update(DEFINITIONS.get("mopup", {}))

        return context


class HealthFacilityMopUpView(ListView):
    """Mopup view."""

    context_object_name = "mopup_locations"
    template_name = "health-facility-mop-up.html"
    queryset = Location.objects.filter(level="ta", target=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["site_name"] = "Mop-up"
        context["district"] = get_object_or_404(
            Location, pk=self.kwargs["district"]
        )
        context[self.context_object_name] = [
            location
            for location in context[self.context_object_name]
            if location.structures_to_mopup > 0
        ]
        print(context)

        # show definitions legend for mopup
        context.update(DEFINITIONS["mopup"])
        active_site = "IRS"
        context.update(DEFINITIONS["mopup"][active_site])

        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(parent__parent_id=self.kwargs["district"])
        )
