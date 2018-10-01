# -*- coding: utf-8 -*-
"""
Sensitization Visit view.
"""

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from mspray.apps.main.models.sensitization_visit import (
    create_sensitization_visit
)


class SensitizationVisitViewSet(
    mixins.CreateModelMixin,  # pylint: disable=bad-continuation
    viewsets.GenericViewSet,  # pylint: disable=bad-continuation
):
    """Sensitization visit viewset."""

    def create(self, request, *args, **kwargs):
        create_sensitization_visit(request.data)
        return Response(status=status.HTTP_201_CREATED)
