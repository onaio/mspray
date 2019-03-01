"""views module for reactive IRS"""
import json

from django.conf import settings
from django.http import Http404
from django.views.generic import DetailView, ListView

from rest_framework import mixins, viewsets

from mspray.apps.main.definitions import DEFINITIONS
from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.query import get_location_qs
from mspray.apps.main.serializers.target_area import TargetAreaSerializer
from mspray.apps.main.utils import parse_spray_date
from mspray.apps.main.views.target_area import (CHWHouseholdsViewSet,
                                                TargetAreaViewSet)
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

        if self.object.level == "chw":
            serializer_class = CHWLocationSerializer
            viewset_class = CHWLocationViewSet

            hhview = CHWHouseholdsViewSet.as_view({"get": "retrieve"})
            response = hhview(
                self.request,
                pk=loc.pk,
                bgeom=bgeom,
                spray_date=spray_date,
                format="geojson",
            )
            response.render()
            hh_geojson = response.content.decode()
        else:
            serializer_class = TargetAreaSerializer
            viewset_class = TargetAreaViewSet

            loc = get_location_qs(Location.objects.filter(pk=loc.pk)).first()
            chw_objects = Location.objects.filter(parent=loc, level="chw")
            hh_geojson = json.dumps(
                GeoCHWLocationSerializer(chw_objects, many=True).data)

        serializer = serializer_class(loc, context={"request": self.request})
        context["target_data"] = serializer.data

        view = viewset_class.as_view({"get": "retrieve"})
        response = view(self.request, pk=loc.pk, format="geojson")
        response.render()
        context["ta_geojson"] = response.content.decode()

        context["hh_geojson"] = hh_geojson

        context["not_sprayable_value"] = getattr(
            settings, "NOT_SPRAYABLE_VALUE", "noteligible")
        context["not_sprayed_reasons"] = json.dumps(
            settings.MSPRAY_UNSPRAYED_REASON_OTHER)
        context["spray_date"] = spray_date

        return context


class CHWListView(SiteNameMixin, ListView):
    """
    View for listing CHW locations grouped by their parents
    """

    template_name = "reactive_irs/list.html"
    model = Location
    slug_field = "pk"

    def get_queryset(self):
        """Get queryset"""
        return (super().get_queryset().filter(
            level="chw", target=True, parent__pk=self.location_id))

    def get_context_data(self, **kwargs):
        """Get context data"""
        context = super().get_context_data(**kwargs)

        object_list = context["object_list"]
        serializer = CHWLocationSerializer(object_list, many=True)

        context.update(DEFINITIONS["ta"])
        context["item_list"] = serializer.data
        context["location"] = self.location

        return context

    # pylint: disable=attribute-defined-outside-init
    def dispatch(self, *args, **kwargs):
        """ Custom dispatch method """
        self.location_id = self.kwargs.get(self.slug_field)
        try:
            self.location = Location.objects.get(pk=self.location_id)
        except Location.DoesNotExist:
            raise Http404
        else:
            return super().dispatch(*args, **kwargs)
