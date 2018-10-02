# -*- coding: utf-8 -*-
"""Mop-up view module.
"""
from django.views.generic import TemplateView


class MopUpView(TemplateView):
    """Mopup view.
    """
    template_name = "mop-up.html"
