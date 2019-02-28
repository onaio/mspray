"""views module for reactive IRS"""
import json

from django.conf import settings
from django.views.generic import DetailView

from rest_framework import mixins, viewsets

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.query import get_location_qs
from mspray.apps.main.utils import parse_spray_date
from mspray.apps.main.views.target_area import CHWHouseholdsViewSet
from mspray.apps.reactive.irs.serializers import (CHWLocationSerializer,
                                                  GeoCHWLocationSerializer)


class CHWLocationViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = get_location_qs(Location.objects.filter(level="chw"))
    serializer_class = CHWLocationSerializer

    def get_serializer_class(self):
        if self.format_kwarg == "geojson":
            return GeoCHWLocationSerializer

        return super().get_serializer_class()


class CHWLocationMapView(SiteNameMixin, DetailView):
    """Map view for Community Health Worker (CHW) locations"""

    template_name = "reactive_irs/map.html"
    model = Location
    slug_field = "pk"

    def get_queryset(self):
        """Get queryset method"""
        return get_location_qs(super().get_queryset().filter(target=True))

    def get_context_data(self, **kwargs):
        """Get context data"""
        context = super().get_context_data(**kwargs)

        bgeom = settings.HH_BUFFER and settings.OSM_SUBMISSIONS
        spray_date = parse_spray_date(self.request)
        loc = context["object"]

        serializer = CHWLocationSerializer(
            loc, context={"request": self.request})

        context["target_data"] = serializer.data

        response = CHWLocationViewSet.as_view({
            "get": "retrieve"
        })(self.request, pk=loc.pk, format="geojson")
        response.render()
        context["not_sprayable_value"] = getattr(
            settings, "NOT_SPRAYABLE_VALUE", "noteligible")
        context["ta_geojson"] = response.content.decode()

        hhview = CHWHouseholdsViewSet.as_view({"get": "retrieve"})
        response = hhview(
            self.request,
            pk=loc.pk,
            bgeom=bgeom,
            spray_date=spray_date,
            format="geojson",
        )
        response.render()
        context["hh_geojson"] = response.content.decode()

        context["not_sprayed_reasons"] = json.dumps(
            settings.MSPRAY_UNSPRAYED_REASON_OTHER)

        return context
