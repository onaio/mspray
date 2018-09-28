# -*- coding: utf-8 -*-
"""
Sensitization Visit view.
"""

from django.http import HttpResponse
from django.views.decorators.http import require_POST

from mspray.apps.main.models.sensitization_visit import (
    create_sensitization_visit
)


@require_POST
def index(request):
    """Create a sensitization visit record view."""
    create_sensitization_visit(request.POST)
    return HttpResponse(status=201)
