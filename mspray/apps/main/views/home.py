# -*- coding: utf-8 -*-
"""Spray effectiveness dashboard."""
import csv
import json

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.exports import detailed_spray_area_data
from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location, WeeklyReport
from mspray.apps.main.query import get_location_qs
from mspray.apps.main.serializers import DistrictSerializer
from mspray.apps.main.serializers.target_area import (
    GeoTargetAreaSerializer,
    TargetAreaQuerySerializer,
    TargetAreaSerializer,
    count_duplicates,
    get_duplicates,
)
from mspray.apps.main.utils import get_location_dict, parse_spray_date
from mspray.apps.main.views.sprayday import get_not_targeted_within_geom
from mspray.apps.main.views.target_area import (
    TargetAreaHouseholdsViewSet,
    TargetAreaViewSet,
)

NOT_SPRAYABLE_VALUE = settings.NOT_SPRAYABLE_VALUE
ENABLE_REVEAL = getattr(settings, "ENABLE_REVEAL", False)


class SprayAreaBuffer:  # pylint: disable=too-few-public-methods
    """
    A file object like class that implements the write operation.
    """

    def write(self, value):  # pylint: disable=no-self-use
        """
        Returns the value passed to it.
        """
        return value


class DistrictView(SiteNameMixin, ListView):
    """Spray Effectiveness landing page - lists districts."""

    template_name = "home/district.html"
    model = Location
    slug_field = "pk"

    def get_template_names(self):
        """get template names"""
        if ENABLE_REVEAL:
            return ["reveal/district.html"]

        return [self.template_name]

    def get_queryset(self):
        queryset = super(DistrictView, self).get_queryset().filter(target=True)
        location_id = self.kwargs.get(self.slug_field)
        if location_id is not None:
            queryset = queryset.filter(parent__pk=location_id)
        else:
            queryset = queryset.filter(parent=None).order_by("name")

        return get_location_qs(queryset)

    def get_context_data(self, **kwargs):  # pylint: disable=R0912,R0914,R0915
        context = super(DistrictView, self).get_context_data(**kwargs)

        not_targeted = None

        queryset = (context["object_list"].extra(
            select={
                "xmin": 'ST_xMin("main_location"."geom")',
                "ymin": 'ST_yMin("main_location"."geom")',
                "xmax": 'ST_xMax("main_location"."geom")',
                "ymax": 'ST_yMax("main_location"."geom")',
            }).values(
                "pk",
                "code",
                "level",
                "name",
                "parent",
                "structures",
                "xmin",
                "ymin",
                "xmax",
                "ymax",
                "num_of_spray_areas",
                "num_new_structures",
                "total_structures",
                "visited",
                "sprayed",
                "is_sensitized",
                "priority",
            ))
        location_id = self.kwargs.get(self.slug_field)
        if location_id is None:
            serializer_class = DistrictSerializer
        else:
            level = self.object_list.first().level if self.object_list.first(
            ) else ""
            if level == "RHC":
                serializer_class = DistrictSerializer
            else:
                serializer_class = (TargetAreaQuerySerializer
                                    if settings.SITE_NAME == "namibia" else
                                    TargetAreaSerializer)
            # no location structures
            try:
                obj = get_object_or_404(Location, pk=location_id, target=True)
            except Location.DoesNotExist:
                pass
            else:
                not_targeted = get_not_targeted_within_geom(obj.geom)[0]
                context["no_location"] = not_targeted
                if obj.level == "district":
                    context["the_district"] = obj
                else:
                    context["the_district"] = (obj.get_ancestors().filter(
                        level="district").first())
        serializer = serializer_class(
            queryset, many=True, context={"request": self.request})
        context["district_list"] = serializer.data
        fields = [
            "structures",
            "visited_total",
            "visited_sprayed",
            "visited_not_sprayed",
            "visited_refused",
            "visited_other",
            "not_visited",
            "found",
            "num_of_spray_areas",
        ]
        totals = {}
        for rec in serializer.data:
            for field in fields:
                try:
                    totals[field] = rec[field] + (totals[field]
                                                  if field in totals else 0)
                except KeyError:
                    pass
        not_captured = getattr(settings, "NOT_CAPTURED", {})
        if not_targeted and not location_id:
            if obj.level != "district":
                not_targeted_fields = [
                    ("visited_total", "found"),
                    ("visited_sprayed", "sprayed"),
                    ("visited_not_sprayed", "not_sprayed"),
                    ("visited_refused", "refused"),
                    ("visited_other", "other"),
                ]
                not_captured_data = not_captured.get(obj.pk)
                if not_captured_data:
                    not_targeted["found"] += not_captured_data
                    not_targeted["sprayed"] += not_captured_data
                for total_field, not_field in not_targeted_fields:
                    try:
                        totals[total_field] += not_targeted[not_field]
                    except KeyError:
                        totals[total_field] = not_targeted[not_field]

        district_code = self.kwargs.get(self.slug_field)
        context.update(get_location_dict(district_code))
        context["district_totals"] = totals
        if not district_code:
            context.update(DEFINITIONS["district"])
        else:
            loc = context.get("district")
            level = "RHC" if loc.level == "district" else "ta"
            context.update(DEFINITIONS[level])

        return context


class TargetAreaView(SiteNameMixin, DetailView):
    """Map view."""

    template_name = "home/map.html"
    model = Location
    slug_field = "pk"

    def get_queryset(self):

        return get_location_qs(
            super(TargetAreaView, self).get_queryset().filter(target=True))

    def get_context_data(self, **kwargs):
        context = super(TargetAreaView, self).get_context_data(**kwargs)
        serializer_class = (TargetAreaQuerySerializer
                            if settings.SITE_NAME == "namibia" else
                            TargetAreaSerializer)
        location = context["object"]
        if location.level == "RHC":
            location = get_location_qs(
                Location.objects.filter(pk=location.pk), "RHC").first()
        serializer = serializer_class(
            location, context={"request": self.request})
        context["target_data"] = serializer.data
        spray_date = parse_spray_date(self.request)
        if spray_date:
            context["spray_date"] = spray_date
        is_spatial = (settings.MSPRAY_SPATIAL_QUERIES
                      or context["object"].geom is not None)

        if is_spatial:
            view = TargetAreaViewSet.as_view({"get": "retrieve"})
            response = view(
                self.request, pk=context["object"].pk, format="geojson")
            response.render()
            context["not_sprayable_value"] = NOT_SPRAYABLE_VALUE
            context["ta_geojson"] = response.content.decode()

            if self.object.level in ["district", "RHC"]:
                context["hh_geojson"] = json.dumps(
                    GeoTargetAreaSerializer(
                        get_location_qs(self.object.location_set.all(),
                                        self.object.level),
                        many=True,
                        context={
                            "request": self.request
                        },
                    ).data)
            else:
                loc = context["object"]
                hhview = TargetAreaHouseholdsViewSet.as_view({
                    "get": "retrieve"
                })
                response = hhview(
                    self.request,
                    pk=loc.pk,
                    bgeom=settings.HH_BUFFER and settings.OSM_SUBMISSIONS,
                    spray_date=spray_date,
                    format="geojson",
                )
                response.render()
                context["hh_geojson"] = response.content.decode()
                sprayed_duplicates = list(
                    get_duplicates(loc, True, spray_date))
                not_sprayed_duplicates = list(
                    get_duplicates(loc, False, spray_date))
                context["sprayed_duplicates_data"] = json.dumps(
                    sprayed_duplicates)
                context["sprayed_duplicates"] = count_duplicates(
                    loc, True, spray_date)
                context["not_sprayed_duplicates_data"] = json.dumps(
                    not_sprayed_duplicates)
                context["not_sprayed_duplicates"] = count_duplicates(
                    loc, False)

        context["districts"] = (Location.objects.filter(
            parent=None).values_list("id", "code", "name").order_by("name"))

        context.update({"map_menu": True})
        context.update(get_location_dict(self.object.pk))
        context["not_sprayed_reasons"] = json.dumps(
            settings.MSPRAY_UNSPRAYED_REASON_OTHER)

        return context


class SprayAreaView(SiteNameMixin, ListView):
    """Spray area tables."""

    template_name = "home/sprayareas.html"
    model = Location
    slug_field = "pk"

    def get_queryset(self):

        return get_location_qs(
            super(SprayAreaView, self).get_queryset().filter(
                level="ta", target=True))

    def get_context_data(self, **kwargs):
        context = super(SprayAreaView, self).get_context_data(**kwargs)
        queryset = (context["object_list"].extra(
            select={
                "xmin": 'ST_xMin("main_location"."geom")',
                "ymin": 'ST_yMin("main_location"."geom")',
                "xmax": 'ST_xMax("main_location"."geom")',
                "ymax": 'ST_yMax("main_location"."geom")',
            }).values(
                "pk",
                "code",
                "level",
                "name",
                "parent",
                "structures",
                "xmin",
                "ymin",
                "xmax",
                "ymax",
                "num_of_spray_areas",
                "num_new_structures",
                "total_structures",
                "parent__name",
                "parent__parent__name",
                "parent__parent__pk",
                "parent__pk",
                "is_sensitized",
            ).order_by("parent__parent__name", "parent__name", "name"))
        if self.request.GET.get("format") != "csv":
            serializer_class = TargetAreaSerializer
            serializer = serializer_class(
                queryset, many=True, context={"request": self.request})
            context["district_list"] = serializer.data
        context["qs"] = queryset
        context.update(get_location_dict(None))
        context.update(DEFINITIONS["ta"])

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get("format") == "csv":

            def calc_percentage(numerator, denominator):
                """
                Returns the percentage of the given values, empty string on
                exceptions.
                """
                try:
                    denominator = float(denominator)
                    numerator = float(numerator)
                except ValueError:
                    return ""

                if denominator == 0:
                    return ""

                return round((numerator * 100) / denominator)

            def _data():
                yield [
                    "District",
                    "Health Centre",
                    "Spray Area",
                    "Structures on Ground",
                    "Found",
                    "Visited Sprayed",
                    "Spray Effectiveness",
                    "Found Coverage",
                    "Sprayed Coverage",
                ]
                previous_rhc = None
                not_captured = getattr(settings, "NOT_CAPTURED", {})
                for value in context.get("qs").iterator():
                    district = TargetAreaSerializer(
                        value, context=context).data
                    if previous_rhc is None:
                        previous_rhc = district
                    if previous_rhc.get("rhc") != district.get("rhc"):
                        not_targeted = get_not_targeted_within_geom(
                            Location.objects.get(
                                pk=previous_rhc.get("rhc_pk")).geom)[0]
                        not_captured_data = not_captured.get(
                            previous_rhc.get("rhc_pk"))
                        if not_captured_data:
                            not_targeted["found"] += not_captured_data
                            not_targeted["sprayed"] += not_captured_data
                        yield [
                            previous_rhc.get("district"),
                            previous_rhc.get("rhc"),
                            "Not in Target Area",
                            "",
                            not_targeted.get("found"),
                            not_targeted.get("sprayed"),
                            "",
                            "",
                            calc_percentage(
                                not_targeted.get("sprayed"),
                                not_targeted.get("found")),
                        ]
                        previous_rhc = district

                    yield [
                        district.get("district"),
                        district.get("rhc"),
                        district.get("district_name"),
                        district.get("structures"),
                        district.get("found"),
                        district.get("visited_sprayed"),
                        calc_percentage(
                            district.get("visited_sprayed"),
                            district.get("structures")),
                        calc_percentage(
                            district.get("found"), district.get("structures")),
                        calc_percentage(
                            district.get("visited_sprayed"),
                            district.get("found")),
                    ]

            sprayarea_buffer = SprayAreaBuffer()
            writer = csv.writer(sprayarea_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in _data()),
                content_type="text/csv")
            response[
                "Content-Disposition"
            ] = 'attachment; filename="sprayareas.csv"'

            return response

        return super(SprayAreaView, self).render_to_response(
            context, **response_kwargs)


class DetailedCSVView(SiteNameMixin, ListView):
    """
    Downloads CSV with details target area information
    provided by TargetAreaRichSerializer
    """

    template_name = "home/sprayareas.html"
    model = Location

    def get_queryset(self):
        queryset = super(DetailedCSVView, self).get_queryset()
        return queryset.filter(level="ta", target=True).order_by("name")

    def render_to_response(self, context, **response_kwargs):
        filename = "detailed_sprayareas.csv"
        if default_storage.exists(filename):
            with default_storage.open(filename) as file_pointer:
                response = HttpResponse(
                    file_pointer.read(), content_type="text/csv")
        else:
            sprayarea_buffer = SprayAreaBuffer()
            writer = csv.writer(sprayarea_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in detailed_spray_area_data(
                    queryset=self.get_queryset())),
                content_type="text/csv",
            )
        response[
            "Content-Disposition"] = 'attachment; filename="%s"' % filename

        return response


class WeeklyReportView(SiteNameMixin, ListView):
    """Weekly Report tables and CSV."""

    template_name = "home/sprayareas.html"
    model = WeeklyReport
    slug_field = "pk"

    def get_queryset(self):
        queryset = super(WeeklyReportView, self).get_queryset()

        return (queryset.filter(
            location__level="district").prefetch_related().order_by(
                "week_number", "location__name"))

    def get_context_data(self, **kwargs):
        context = super(WeeklyReportView, self).get_context_data(**kwargs)
        context["qs"] = context["object_list"]
        weeks = list(context["object_list"].values_list(
            "week_number", flat=True).order_by("week_number").distinct())
        context["weeks"] = dict(
            list(zip(weeks, [i for i in range(1,
                                              len(weeks) + 1)])))

        return context

    def render_to_response(self, context, **response_kwargs):
        def calc_percentage(numerator, denominator):
            """
            Returns the percentage of the given values, empty string on
            exceptions.
            """
            try:
                denominator = float(denominator)
                numerator = float(numerator)
            except ValueError:
                return ""

            if denominator == 0:
                return ""

            return round((numerator * 100) / denominator)

        def _data():
            yield [
                "Week #",
                "Calendar Week #",
                "District",
                "Eligible Spray Areas",
                "Spray Areas Visited",
                "Spray Areas Visited %",
                "Spray Areas Sprayed Effectively",
                "Spray Areas Sprayed Effectively %",
            ]
            for district in context.get("qs"):
                yield [
                    context["weeks"][district.week_number],
                    district.week_number,
                    district.location.name,
                    district.location.num_of_spray_areas,
                    district.visited,
                    calc_percentage(district.visited,
                                    district.location.num_of_spray_areas),
                    district.sprayed,
                    calc_percentage(district.sprayed,
                                    district.location.visited),
                ]

        sprayarea_buffer = SprayAreaBuffer()
        writer = csv.writer(sprayarea_buffer)
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in _data()), content_type="text/csv")
        response[
            "Content-Disposition"] = 'attachment; filename="weeklyreport.csv"'

        return response
