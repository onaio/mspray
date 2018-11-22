# -*- coding: utf-8 -*-
"""MDA view module.
"""
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.models import Location


class MDAView(ListView):
    """MDA view."""

    template_name = "mda-location.html"
    queryset = Location.objects.filter(level="district", target=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["site_name"] = "MDA"
        context["ENABLE_MDA"] = True

        # show definitions legend for mda
        context.update(DEFINITIONS.get("mda", {}))

        return context


class MDALocationView(ListView):
    """MDA Location view."""

    template_name = "mda-location.html"
    queryset = Location.objects.filter(target=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["site_name"] = "MDA"
        context["mda_location"] = get_object_or_404(
            Location, pk=self.kwargs["location"], target=True
        )
        context["ENABLE_MDA"] = True

        # show definitions legend for mda
        context.update(DEFINITIONS.get("mda", {}))

        return context

    def get_queryset(self):
        return super().get_queryset().filter(parent_id=self.kwargs["location"])
