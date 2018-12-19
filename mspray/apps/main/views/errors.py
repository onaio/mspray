# -*- coding: utf-8 -*
"""Custom 404 view."""
from django.shortcuts import render


def error_404(request):
    """Render custom template."""
    data = {}
    if request.path.startswith('/mda/'):
        template_name = '/templates/404.html'
    elif request.path.startswith('/reveal/'):
        template_name = '/templates/404.html'
    return render(
        request, template_name, data)
