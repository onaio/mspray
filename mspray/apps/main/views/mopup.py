# -*- coding: utf-8 -*-
"""Mop-up view module.
"""
from django.views.generic import ListView

from mspray.apps.main.models import Location


class MopUpView(ListView):
    """Mopup view.
    """
    context_object_name = 'mopup_locations'
    template_name = "mop-up.html"
    queryset = Location.objects.filter(level='district')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'Mop-up'

        return context
