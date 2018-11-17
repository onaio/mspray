# -*- coding: utf-8 -*-
"""Map views"""
import json

from django.conf import settings
from django.views.generic import DetailView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.query import get_location_qs
from mspray.apps.main.serializers.target_area import (
    GeoTargetAreaSerializer,
    TargetAreaQuerySerializer,
    TargetAreaSerializer,
    count_duplicates,
    get_duplicates,
)
from mspray.apps.main.utils import get_location_dict, parse_spray_date
from mspray.apps.main.views.target_area import (
    TargetAreaHouseholdsViewSet,
    TargetAreaViewSet,
)


class MapView(SiteNameMixin, DetailView):
    """Map View"""

    template_name = "map.html"
    model = Location
    slug_field = "pk"

    def get_queryset(self):

        return get_location_qs(super(MapView, self).get_queryset())

    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)
        serializer_class = (
            TargetAreaQuerySerializer
            if settings.SITE_NAME == "namibia"
            else TargetAreaSerializer
        )
        location = context["object"]
        if location.level == "RHC":
            location = get_location_qs(
                Location.objects.filter(pk=location.pk), "RHC"
            ).first()
        serializer = serializer_class(
            location, context={"request": self.request}
        )
        context["target_data"] = serializer.data
        spray_date = parse_spray_date(self.request)
        if spray_date:
            context["spray_date"] = spray_date
        if settings.MSPRAY_SPATIAL_QUERIES or context["object"].geom:
            response = TargetAreaViewSet.as_view({"get": "retrieve"})(
                self.request, pk=context["object"].pk, format="geojson"
            )
            response.render()
            context["not_sprayable_value"] = getattr(
                settings, "NOT_SPRAYABLE_VALUE", "noteligible"
            )
            context["ta_geojson"] = response.content.decode()
            bgeom = settings.HH_BUFFER and settings.OSM_SUBMISSIONS

            if self.object.level in ["district", "RHC"]:
                data = GeoTargetAreaSerializer(
                    get_location_qs(
                        self.object.location_set.all(), self.object.level
                    ),
                    many=True,
                    context={"request": self.request},
                ).data
                context["hh_geojson"] = json.dumps(data)
            else:
                loc = context["object"]
                hhview = TargetAreaHouseholdsViewSet.as_view(
                    {"get": "retrieve"}
                )
                response = hhview(
                    self.request,
                    pk=loc.pk,
                    bgeom=bgeom,
                    spray_date=spray_date,
                    format="geojson",
                )
                response.render()
                context["hh_geojson"] = response.content.decode()
                sprayed_duplicates = list(
                    get_duplicates(loc, True, spray_date)
                )
                not_sprayed_duplicates = list(
                    get_duplicates(loc, False, spray_date)
                )
                context["sprayed_duplicates_data"] = json.dumps(
                    sprayed_duplicates
                )
                context["sprayed_duplicates"] = count_duplicates(
                    loc, True, spray_date
                )
                context["not_sprayed_duplicates_data"] = json.dumps(
                    not_sprayed_duplicates
                )
                context["not_sprayed_duplicates"] = count_duplicates(
                    loc, False
                )

        context["districts"] = (
            Location.objects.filter(parent=None)
            .values_list("id", "code", "name")
            .order_by("name")
        )

        context.update({"map_menu": True})
        context.update(get_location_dict(self.object.pk))
        context["not_sprayed_reasons"] = json.dumps(
            settings.MSPRAY_UNSPRAYED_REASON_OTHER
        )

        return context
