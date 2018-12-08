# -*- coding=utf-8 -*-
"""
SprayDay viewset module - viewset for IRS HH submissions.
"""
from django.conf import settings
from django.contrib.gis.db.backends.postgis.adapter import PostGISAdapter
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Count
from django.db.utils import IntegrityError
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView

from django_filters import filterset
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location, SprayPoint
from mspray.apps.main.models.spray_day import (
    DATA_ID_FIELD,
    DATE_FIELD,
    SprayDay,
)
from mspray.apps.main.serializers.sprayday import (
    SprayDayNamibiaSerializer,
    SprayDaySerializer,
    SprayDayShapeSerializer,
)
from mspray.apps.main.serializers.target_area import dictfetchall
from mspray.apps.main.utils import (
    add_spray_data,
    delete_cached_target_area_keys,
)

SPATIAL_QUERIES = False

SPRAY_AREA_INDICATOR_SQL = """
SELECT
COALESCE(SUM(CASE WHEN "other" > 0 THEN 1 ELSE 0 END), 0) AS "other",
COALESCE(SUM(CASE WHEN "not_sprayable" > 0 THEN 1 ELSE 0 END), 0) AS "not_sprayable",
COALESCE(SUM(CASE WHEN "found" > 0 THEN 1 ELSE 0 END), 0) AS "found",
COALESCE(SUM(CASE WHEN "sprayed" > 0 THEN 1 ELSE 0 END), 0) AS "sprayed",
COALESCE(SUM(CASE WHEN "new_structures" > 0 THEN 1 ELSE 0 END), 0) AS "new_structures",
COALESCE(SUM(CASE WHEN "not_sprayed" > 0 THEN 1 ELSE 0 END), 0) AS "not_sprayed",
COALESCE(SUM(CASE WHEN "refused" >0 THEN 1 ELSE 0 END), 0) AS "refused"
FROM
(
  SELECT
  SUM(CASE WHEN ("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = true) THEN 0 ELSE 1 END) AS "other",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL) THEN 1 ELSE 0 END) AS "not_sprayable",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'osmstructure:way:id' AND "main_sprayday"."sprayable" = false AND "main_spraypoint"."id" IS NOT NULL) THEN 0 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "found",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "sprayed",
  SUM(CASE WHEN ("main_sprayday"."data" ? 'newstructure/gps' AND "main_sprayday"."sprayable" = true) THEN 1 WHEN ("main_sprayday"."data" ? 'osmstructure:node:id' AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL) THEN 1 WHEN ("main_sprayday"."data" ? 'osmstructure:node:id' AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NULL AND "main_sprayday"."was_sprayed" = true) THEN 1 ELSE 0 END) AS "new_structures",
  SUM(CASE WHEN ("main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "not_sprayed",
  SUM(CASE WHEN ("main_sprayday"."data" @> '{"osmstructure:notsprayed_reASon": "refused"}' AND "main_sprayday"."sprayable" = true AND "main_spraypoint"."id" IS NOT NULL AND "main_sprayday"."was_sprayed" = false) THEN 1 ELSE 0 END) AS "refused"
  FROM "main_sprayday"
  LEFT OUTER JOIN "main_spraypoint" ON ("main_sprayday"."id" = "main_spraypoint"."sprayday_id") WHERE ("main_sprayday"."location_id" IS NULL) GROUP BY "main_sprayday"."id"
) AS "sub_query";
"""  # noqa


def get_not_targeted_within_geom(geom):
    """
    Takes an object wiht a geom field and runs a query to find spray day
    objects that are within that geom field
    """
    cursor = connection.cursor()
    sql = SPRAY_AREA_INDICATOR_SQL.replace(
        '"main_sprayday"."location_id" IS NULL',
        '"main_sprayday"."location_id" IS NULL AND '
        'ST_Within("main_sprayday"."geom", {})'.format(
            PostGISAdapter(geom).getquoted()
        ),
    )
    cursor.execute(sql)
    return dictfetchall(cursor)


def get_num_sprayed_for_districts():
    """
    Returns a dict with the number of unique sprayed structures per district.
    """
    return dict(
        list(
            SprayPoint.objects.filter(
                sprayday__location__isnull=False, sprayday__was_sprayed=True
            )
            .values("sprayday__location__parent__parent__name")
            .annotate(sprayed=Count("id"))
            .values_list("sprayday__location__parent__parent__name", "sprayed")
        )
    )


class SprayDateFilter(filterset.FilterSet):
    """
    Spray date filter.
    """

    class Meta:
        model = SprayDay
        fields = {"spray_date": ["exact", "lte"]}


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
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ("spray_date",)
    ordering_fields = ("spray_date",)
    ordering = ("spray_date",)
    filter_class = SprayDateFilter

    def get_serializer_class(self):
        if settings.OSM_SUBMISSIONS:
            return SprayDayShapeSerializer

        if settings.SITE_NAME == "namibia":
            return SprayDayNamibiaSerializer

        return super(SprayDayViewSet, self).get_serializer_class()

    def filter_queryset(self, queryset):
        targetid = self.request.query_params.get("target_area")

        if targetid:
            target = get_object_or_404(Location, pk=targetid)
            if SPATIAL_QUERIES:  # settings.MSPRAY_SPATIAL_QUERIES:
                queryset = queryset.filter(geom__coveredby=target.geom)
            else:
                if target.parent is None:
                    queryset = queryset.filter(location__parent=target)
                else:
                    queryset = queryset.filter(location=target)

        if getattr(settings, "MSPRAY_UNIQUE_FIELD", None):
            queryset = queryset.filter(
                pk__in=SprayPoint.objects.values("sprayday")
            )

        return super(SprayDayViewSet, self).filter_queryset(queryset)

    def create(self, request, *args, **kwargs):
        has_id = request.data.get(DATA_ID_FIELD)
        spray_date = request.data.get(DATE_FIELD)

        if not has_id or not spray_date:
            data = {
                "error": _(
                    "Not a valid submission: _id - %s, date - %s"
                    % (has_id, spray_date)
                )
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
                    "success": _(
                        "Successfully imported submission with"
                        " submission id %(submission_id)s."
                        % {"submission_id": has_id}
                    )
                }
                status_code = status.HTTP_201_CREATED
                delete_cached_target_area_keys(sprayday)

        return Response(data, status=status_code)

    def list(self, request, *args, **kwargs):
        if request.query_params.get("dates_only") == "true":
            # pylint: disable=attribute-defined-outside-init
            self.object_list = self.filter_queryset(self.get_queryset())
            data = self.object_list.values_list(
                "spray_date", flat=True
            ).distinct()

            return Response(data)

        return super(SprayDayViewSet, self).list(request, *args, **kwargs)


class NoLocationSprayDayView(SiteNameMixin, TemplateView):
    """
    Found structures not in a target area.
    """

    template_name = "home/no_location_spraydays.html"

    def get_context_data(self, **kwargs):
        context = super(NoLocationSprayDayView, self).get_context_data(
            **kwargs
        )
        context.update(DEFINITIONS["ta"])

        districts = Location.objects.filter(level="district").order_by("name")

        cursor = connection.cursor()

        not_captured = getattr(settings, "NOT_CAPTURED", {})
        not_captured_total = 0
        # per district
        district_data = {}
        for district in districts:
            result = get_not_targeted_within_geom(district.geom)
            district_data[district] = result[0]
            not_captured_data = not_captured.get(district.pk)
            if not_captured_data:
                district_data[district]["found"] += not_captured_data
                district_data[district]["sprayed"] += not_captured_data
                not_captured_total += not_captured_data

        # totals
        cursor = connection.cursor()
        cursor.execute(SPRAY_AREA_INDICATOR_SQL)

        total_results = dictfetchall(cursor)[0]
        total_results["found"] += not_captured_total
        total_results["sprayed"] += not_captured_total
        context["district_data"] = district_data
        context["total"] = total_results
        context["district_sprayed"] = get_num_sprayed_for_districts()

        context["no_location"] = {
            "found": (
                total_results["found"]
                - sum(
                    [
                        v["found"]
                        for k, v in district_data.items()
                        if v["found"]
                    ]
                )
            ),
            "sprayed": (
                total_results["sprayed"]
                - sum(
                    [
                        v["sprayed"]
                        for k, v in district_data.items()
                        if v["sprayed"]
                    ]
                )
            ),
            "new_structures": (
                total_results["new_structures"]
                - sum(
                    [
                        v["new_structures"]
                        for k, v in district_data.items()
                        if v["new_structures"]
                    ]
                )
            ),
        }

        return context
