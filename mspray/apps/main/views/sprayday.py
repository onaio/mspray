# -*- coding=utf-8 -*-
"""
SprayDay viewset module - viewset for IRS HH submissions.
"""
import django_filters
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.http import QueryDict

from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from mspray.apps.main.models import Location, SprayPoint
from mspray.apps.main.models.spray_day import (DATA_ID_FIELD, DATE_FIELD,
                                               SprayDay)
from mspray.apps.main.serializers.sprayday import (
    SprayDayNamibiaSerializer, SprayDaySerializer, SprayDayShapeSerializer)
from mspray.apps.main.utils import (add_spray_data,
                                    delete_cached_target_area_keys)

SPATIAL_QUERIES = False


class SprayDateFilter(django_filters.FilterSet):
    """
    Spray date filter.
    """

    class Meta:
        model = SprayDay
        fields = {'spray_date': ['exact', 'lte']}


# pylint: disable=too-many-ancestors
class SprayDayViewSet(viewsets.ModelViewSet):
    """
    List of households that have been sprayed.

    Query Parameters:
    - `day` - filter list of sprayed points for a specific day
    - `target_area` - filter spray points for a specific target
    - `ordering` - you can order by day field e.g `ordering=day` or \
    `ordering=-day`
    """
    queryset = SprayDay.objects.filter()
    serializer_class = SprayDaySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('spray_date', )
    ordering_fields = ('spray_date', )
    ordering = ('spray_date', )
    filter_class = SprayDateFilter

    def get_serializer_class(self):
        if settings.OSM_SUBMISSIONS:
            return SprayDayShapeSerializer

        if settings.SITE_NAME == 'namibia':
            return SprayDayNamibiaSerializer

        return super(SprayDayViewSet, self).get_serializer_class()

    def filter_queryset(self, queryset):
        targetid = self.request.query_params.get('target_area')

        if targetid:
            target = get_object_or_404(Location, pk=targetid)
            if SPATIAL_QUERIES:  # settings.MSPRAY_SPATIAL_QUERIES:
                queryset = queryset.filter(geom__coveredby=target.geom)
            else:
                if target.parent is None:
                    queryset = queryset.filter(location__parent=target)
                else:
                    queryset = queryset.filter(location=target)

        if getattr(settings, 'MSPRAY_UNIQUE_FIELD', None):
            queryset = queryset.filter(
                pk__in=SprayPoint.objects.values('sprayday'))

        return super(SprayDayViewSet, self).filter_queryset(queryset)

    def create(self, request, *args, **kwargs):
        has_id = request.data.get(DATA_ID_FIELD)
        spray_date = request.data.get(DATE_FIELD)

        if not has_id or not spray_date:
            data = {
                "error":
                _("Not a valid submission: _id - %s, date - %s" % (has_id,
                                                                   spray_date))
            }
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            request_data = request.data
            if isinstance(request.data, QueryDict):
                request_data = request.data.dict()

            try:
                sprayday = add_spray_data(request_data)
            except ValidationError as error:
                data = {"error": "%s" % error}
                status_code = status.HTTP_400_BAD_REQUEST
            except IntegrityError as error:
                data = {"error": "%s" % error}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                data = {
                    "success":
                    _("Successfully imported submission with"
                      " submission id %(submission_id)s." %
                      {'submission_id': has_id})
                }
                status_code = status.HTTP_201_CREATED
                delete_cached_target_area_keys(sprayday)

        return Response(data, status=status_code)

    def list(self, request, *args, **kwargs):
        if request.query_params.get('dates_only') == 'true':
            # pylint: disable=attribute-defined-outside-init
            self.object_list = self.filter_queryset(self.get_queryset())
            data = self.object_list\
                .values_list('spray_date', flat=True).distinct()

            return Response(data)

        return super(SprayDayViewSet, self).list(request, *args, **kwargs)
