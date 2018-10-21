# -*- coding: utf-8 -*-
"""
Decision view.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mspray.apps.main.models.decision import create_decision_visit


class DecisionView(APIView):
    """Decision viewset."""

    def post(self, request):
        """Handle a Decision submission."""
        create_decision_visit(request.data)
        return Response(status=status.HTTP_201_CREATED)
