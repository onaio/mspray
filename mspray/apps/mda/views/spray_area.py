# -*- coding: utf-8 -*-
"""Spray area views."""
import csv

from django.http import StreamingHttpResponse
from django.views.generic import ListView

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location


class SprayAreaView(SiteNameMixin, ListView):
    """List all spray areas via CSV download and HTML."""

    template_name = "sprayareas.html"
    queryset = (
        Location.objects.filter(level="ta", target=True)
        .order_by("parent__parent__name", "parent__name", "name")
        .select_related("parent__parent")
        .only(
            "level",
            "name",
            "structures",
            "parent__name",
            "parent__parent__name",
        )
    )

    def get_context_data(self, **kwargs):
        context = super(SprayAreaView, self).get_context_data(**kwargs)
        context.update(DEFINITIONS["ta"])
        context["format"] = self.kwargs.get("format")

        return context

    def render_to_response(self, context, **response_kwargs):
        if "csv" in [self.request.GET.get("format"), context["format"]]:

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

            class SprayAreaBuffer:  # pylint: disable=too-few-public-methods
                """
                A file object like class that implements the write operation.
                """

                def write(self, value):  # pylint: disable=no-self-use
                    """
                    Returns the value passed to it.
                    """
                    return value

            def _data():
                yield [
                    "District",
                    "Health Centre",
                    "Spray Area",
                    "Eligible Structures on Ground",
                    "Structures Found",
                    "Structures Received",
                    "Population Received Treatment",
                    "Population Eligible",
                    "Spray Effectiveness",
                    "Found Coverage",
                    "Sprayed Coverage",
                    "Population Received Success Rate",
                    "Community Ready?",
                    "Mobilised?",
                ]
                previous_rhc = None
                for location in context.get("object_list").iterator():
                    if previous_rhc != location.parent:
                        previous_rhc = location.parent

                    yield [
                        location.parent.parent.name,
                        location.parent.name,
                        location.name,
                        location.mda_structures,
                        location.mda_found,
                        location.mda_received,
                        location.population_treatment,
                        location.population_eligible,
                        calc_percentage(
                            location.mda_received, location.mda_structures
                        ),
                        calc_percentage(
                            location.mda_found, location.mda_structures
                        ),
                        calc_percentage(
                            location.mda_received, location.mda_found
                        ),
                        calc_percentage(
                            location.population_treatment,
                            location.population_eligible,
                        ),
                        location.sensitized,
                        location.mobilised,
                    ]

            sprayarea_buffer = SprayAreaBuffer()
            writer = csv.writer(sprayarea_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in _data()),
                content_type="text/csv",
            )
            response[
                "Content-Disposition"
            ] = 'attachment; filename="sprayareas.csv"'

            return response

        return super(SprayAreaView, self).render_to_response(
            context, **response_kwargs
        )
