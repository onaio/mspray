# -*- coding: utf-8 -*
"""Custom 404 error page."""
from django.shortcuts import render


def error_404(request):
    """Render custom template."""
    data = {}
    return render(
        request, 'mspray/apps/main/templates/home/error_404.html', data)
