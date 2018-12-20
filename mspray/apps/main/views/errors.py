# -*- coding: utf-8 -*
"""Custom 404 view."""
from django.shortcuts import render


def error_404(request, *args, **argv):
    """Render custom template."""
    data = {}
    template_name = '404.html'
    response = render(request, template_name, data)
    response.status_code = 404
    return response
