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
from mspray.apps.main.utils import parse_spray_date
from mspray.apps.main.views.home import DistrictView, TargetAreaView
from mspray.apps.main.views.target_area import CHWHouseholdsViewSet
from mspray.apps.reactive.irs.serializers import (
    CHWinTargetAreaSerializer,
    CHWLocationSerializer,
    GeoCHWinTargetAreaSerializer,
    GeoCHWLocationSerializer,
)

TA_LEVEL = getattr(settings, "MSPRAY_TA_LEVEL", "ta")
CHW_LEVEL = getattr(settings, "MSPRAY_REACTIVE_IRS_CHW_LOCATION_LEVEL", "chw")
HOME_PARENT_ID = getattr(settings, "MSPRAY_REACTIVE_IRS_HOME_PARENT")
IRS = getattr(settings, "MSPRAY_REACTIVE_IRS_DEFINITIONS", "irs")


class CHWContextMixin(ListView):
    """
    Processes the context data to include objects from the
    CHWLocationSerializer
    """

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get context data"""
        context = super().get_context_data(object_list=object_list, **kwargs)

        object_list = context["object_list"]
        serializer = CHWLocationSerializer(object_list, many=True)

        context["item_list"] = serializer.data

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
                    totals[field] = rec[field] + (
                        totals[field] if field in totals else 0
                    )
                except KeyError:
                    pass

        context["chw_totals"] = totals
        context["location"] = self.location
        context["is_home_page"] = self.is_home_page

        context.update(DEFINITIONS[IRS])

        return context


class CHWLocationViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Community Health Worker (CHW) location viewset class"""

    queryset = get_location_qs(Location.objects.filter(level=CHW_LEVEL))
    serializer_class = CHWLocationSerializer

    def get_serializer_class(self):
        if self.format_kwarg == "geojson":
            return GeoCHWLocationSerializer

        return super().get_serializer_class()


class CHWinLocationViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Community Health Worker (CHW) location viewset class"""

    queryset = get_location_qs(Location.objects.filter(level="district"))
    serializer_class = CHWinTargetAreaSerializer

    def get_serializer_class(self):
        if self.format_kwarg == "geojson":
            return GeoCHWinTargetAreaSerializer

        return super().get_serializer_class()


class CHWLocationMapView(SiteNameMixin, DetailView):
    """Map view for Community Health Worker (CHW) locations"""

    template_name = "reactive_irs/map.html"
    model = Location
    slug_field = "pk"

    def get_queryset(self):
        """Get queryset method"""
        return get_location_qs(super().get_queryset().filter(target=True))

    # pylint: disable=too-many-locals
    def get_context_data(self, **kwargs):
        """Get context data"""
        context = super().get_context_data(**kwargs)

        bgeom = settings.HH_BUFFER and settings.OSM_SUBMISSIONS
        spray_date = parse_spray_date(self.request)
        loc = context["object"]

        context["district_list"] = Location.objects.filter(parent=None)

        if self.object.level == CHW_LEVEL:
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

            context["chw_list"] = Location.objects.filter(
                parent=loc.parent, level=CHW_LEVEL
            )
        else:
            serializer_class = CHWinTargetAreaSerializer
            viewset_class = CHWinLocationViewSet

            loc = get_location_qs(Location.objects.filter(pk=loc.pk)).first()
            chw_objects = Location.objects.filter(parent=loc, level=CHW_LEVEL)
            hh_data = GeoCHWLocationSerializer(chw_objects, many=True).data
            context["chw_list"] = chw_objects
            hh_geojson = json.dumps(hh_data)
        context["tas"] = Location.objects.filter(parent=loc, level="ta").only("pk")

        serializer = serializer_class(loc, context={"request": self.request})
        context["target_data"] = serializer.data

        view = viewset_class.as_view({"get": "retrieve"})
        response = view(self.request, pk=loc.pk, format="geojson")
        response.render()
        context["ta_geojson"] = response.content.decode()

        context["hh_geojson"] = hh_geojson

        context["not_sprayable_value"] = getattr(
            settings, "NOT_SPRAYABLE_VALUE", "noteligible"
        )
        context["not_sprayed_reasons"] = json.dumps(
            settings.MSPRAY_UNSPRAYED_REASON_OTHER
        )
        context["spray_date"] = spray_date
        context.update({"map_menu": True})

        return context


class CHWListView(SiteNameMixin, CHWContextMixin):
    """
    View for listing CHW locations grouped by their parents
    """

    template_name = "reactive_irs/list.html"
    model = Location
    slug_field = "pk"

    def get_queryset(self):
        """Get queryset"""
        return (
            super()
            .get_queryset()
            .filter(level=CHW_LEVEL, target=True, parent__pk=self.location_id)
        )

    # pylint: disable=attribute-defined-outside-init
    def dispatch(self, request, *args, **kwargs):
        """ Custom dispatch method """
        self.is_home_page = False
        self.location_id = self.kwargs.get(self.slug_field)
        try:
            self.location = Location.objects.get(pk=self.location_id)
        except Location.DoesNotExist:
            raise Http404
        else:
            return super().dispatch(request, *args, **kwargs)


class HomeView(SiteNameMixin, CHWContextMixin):
    """
    Displays the home page
    """

    template_name = "reactive_irs/list.html"
    model = Location
    slug_field = "pk"

    def get_queryset(self):
        """Get queryset"""
        return (
            super()
            .get_queryset()
            .filter(level=CHW_LEVEL, target=True, parent=HOME_PARENT_ID)
        )

    # pylint: disable=attribute-defined-outside-init
    def dispatch(self, request, *args, **kwargs):
        """ Custom dispatch method """
        self.location = None
        self.is_home_page = True
        if HOME_PARENT_ID is not None:
            try:
                self.location = Location.objects.get(pk=HOME_PARENT_ID)
            except Location.DoesNotExist:
                raise Http404
        return super().dispatch(request, *args, **kwargs)


class LocationCHWView(SiteNameMixin, ListView):
    """
    Display a list of locations with data pulled from CHWs inside the locations
    """

    template_name = "reactive_irs/list.html"
    model = Location

    def get_queryset(self):
        """Get queryset"""
        return super().get_queryset().filter(target=True, parent=None)

    def get_context_data(self, **kwargs):
        """Get context data"""
        context = super().get_context_data(**kwargs)

        object_list = context["object_list"]
        serializer = CHWinTargetAreaSerializer(object_list, many=True)

        context["item_list"] = serializer.data
        context.update(DEFINITIONS[TA_LEVEL])

        return context


class CHWTargetAreaView(DistrictView):
    """Display target areas inside a CHW location"""

    template_name = "reactive_irs/ta.html"

    def get_context_data(self, **kwargs):
        """Get context data"""
        context = super().get_context_data(**kwargs)
        context.update(DEFINITIONS[IRS])
        return context


class CHWTargetAreaMapView(TargetAreaView):
    """Display map of a single target area"""

    template_name = "reactive_irs/map.html"
