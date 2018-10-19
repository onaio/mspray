# -*- coding: utf-8 -*-
"""
Sensitization Visit view.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mspray.apps.main.models.sensitization_visit import (
    create_sensitization_visit
)


class SensitizationVisitView(APIView):
    """Sensitization visit viewset."""

    def post(self, request):
        """Handle Sensitization visit submissions."""
        create_sensitization_visit(request.data)
        return Response(status=status.HTTP_201_CREATED)
