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
from django.db import connection
from django.views.generic.base import TemplateView

from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location, SprayPoint
from mspray.apps.main.models.spray_day import (DATA_ID_FIELD, DATE_FIELD,
                                               SprayDay)
from mspray.apps.main.serializers.sprayday import (
    SprayDayNamibiaSerializer, SprayDaySerializer, SprayDayShapeSerializer)
from mspray.apps.main.utils import (add_spray_data,
                                    delete_cached_target_area_keys)
from mspray.apps.main.serializers.target_area import dictfetchall

SPATIAL_QUERIES = False

spray_area_indicator_sql = """
SELECT
SUM(CASE WHEN "other" > 0 THEN 1 ELSE 0 END) AS "other",
SUM(CASE WHEN "not_sprayable" > 0 THEN 1 ELSE 0 END) AS "not_sprayable",
SUM(CASE WHEN "found" > 0 THEN 1 ELSE 0 END) AS "found",
SUM(CASE WHEN "sprayed" > 0 THEN 1 ELSE 0 END) AS "sprayed",
SUM(CASE WHEN "new_structures" > 0 THEN 1 ELSE 0 END) AS "new_structures",
SUM(CASE WHEN "not_sprayed" > 0 THEN 1 ELSE 0 END) AS "not_sprayed",
SUM(CASE WHEN "refused" >0 THEN 1 ELSE 0 END) AS "refused" FROM
(
  SELECT
  SUM(CASE WHEN ("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = true) THEN 0 ELSE 1 END) AS "other",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL) THEN 1 ELSE 0 END) AS "not_sprayable",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "found",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "sprayed",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'newstructure/gps' AND "main_sprayday"."sprayable" = true) THEN 1 WHEN ("main_sprayday"."data" ? 'osmstructure:node:id' AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN ("main_sprayday"."data" ? 'osmstructure:node:id' AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "new_structures",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "not_sprayed",
  SUM(CASE WHEN ("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "refused"
  FROM "main_sprayday" LEFT OUTER JOIN "main_spraypoint" ON ("main_sprayday"."id" = "main_spraypoint"."sprayday_id") WHERE ("main_sprayday"."location_id" IS NULL) GROUP BY "main_sprayday"."id"
) AS "sub_query";
"""  # noqa


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


class NoLocationSprayDayView(SiteNameMixin, TemplateView):
    template_name = 'home/no_location_spraydays.html'

    def get_context_data(self, **kwargs):
        context = super(NoLocationSprayDayView,
                        self).get_context_data(**kwargs)
        cursor = connection.cursor()
        cursor.execute(spray_area_indicator_sql)
        results = dictfetchall(cursor)
        context['data'] = results[0]
        return context
