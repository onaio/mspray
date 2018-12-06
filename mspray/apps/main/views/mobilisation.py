# -*- coding: utf-8 -*-
"""Mobilisation view."""
import logging
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mspray.apps.main.models.mobilisation import create_mobilisation_visit

logger = logging.getLogger(__name__)


class MobilisationView(APIView):
    """Mobilisation viewset."""

    def post(self, request):
        """Handle a Mobilisation submission."""
        try:
            create_mobilisation_visit(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            logger.exception("Mobilisation submission already exists.")
            return Response(status=status.HTTP_202_CREATED)
