# -*- coding: utf-8 -*-
"""Mop-up view module.
"""
from django.views.generic import ListView

from mspray.apps.main.models import Location


class MopUpView(ListView):
    """Mopup view.
    """

    context_object_name = "mopup_locations"
    template_name = "mop-up.html"
    queryset = Location.objects.filter(level="district")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = "Mop-up"

        return context


class HealthFacilityMopUpView(ListView):
    """Mopup view.
    """

    context_object_name = "mopup_locations"
    template_name = "health-facility-mop-up.html"
    queryset = Location.objects.filter(level="ta")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = "Mop-up"

        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(parent__parent_id=self.kwargs["district"])
        )
