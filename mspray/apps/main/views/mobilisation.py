# -*- coding: utf-8 -*-
"""
Mobilisation view.
"""

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from mspray.apps.main.models.mobilisation import create_mobilisation_visit


class MobilisationViewSet(
    mixins.CreateModelMixin,  # pylint: disable=bad-continuation
    viewsets.GenericViewSet,  # pylint: disable=bad-continuation
):
    """Mobilisation viewset."""

    def create(self, request, *args, **kwargs):
        create_mobilisation_visit(request.data)
        return Response(status=status.HTTP_201_CREATED)
