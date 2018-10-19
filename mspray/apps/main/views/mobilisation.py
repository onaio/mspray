# -*- coding: utf-8 -*-
"""
Mobilisation view.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mspray.apps.main.models.mobilisation import create_mobilisation_visit


class MobilisationView(APIView):
    """Mobilisation viewset."""

    def post(self, request):
        """Handle a Mobilisation submission."""
        create_mobilisation_visit(request.data)
        return Response(status=status.HTTP_201_CREATED)
