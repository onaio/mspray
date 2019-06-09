"""urls module for Reactive IRS"""
from django.conf.urls import include
from django.urls import path

from rest_framework import routers

from mspray.apps.main.views import (
    districts,
    household,
    household_buffer,
    sprayday,
    target_area,
)
from mspray.apps.reactive.irs import performance
from mspray.apps.reactive.irs.views import (
    CHWListView,
    CHWLocationMapView,
    CHWTargetAreaMapView,
    CHWTargetAreaView,
    HomeView,
)

router = routers.DefaultRouter(trailing_slash=False)  # pylint: disable=C0103

router.register(r"buffers", household_buffer.HouseholdBufferViewSet)
router.register(r"districts", districts.DistrictViewSet, "district")
router.register(r"households", household.HouseholdViewSet)
router.register(r"spraydays", sprayday.SprayDayViewSet)
router.register(r"targetareas", target_area.TargetAreaViewSet)

performance_urls = (  # pylint: disable=C0103
    [
        path("", performance.DistrictPerfomanceView.as_view(), name="districts"),
        path(
            "team-leaders/<int:slug>",
            performance.TeamLeadersPerformanceView.as_view(),
            name="team-leaders",
        ),
        path(
            "spray-operators/<int:slug>/<int:team_leader>/summary",
            performance.SprayOperatorSummaryView.as_view(),
            name="spray-operator-summary",
        ),
        path(
            "spray-operators/<int:slug>/<int:team_leader>/"
            "<int:spray_operator>/daily",
            performance.SprayOperatorDailyView.as_view(),
            name="spray-operator-daily",
        ),
    ],
    "mspray",
)

# pylint: disable=invalid-name
app_name = "reactive_irs"
urlpatterns = [
    path("", HomeView.as_view(), name="reactive_irs_home"),
    path("<int:pk>", CHWListView.as_view(), name="chw_list"),
    path("chw/<int:pk>", CHWTargetAreaView.as_view(), name="ta_list"),
    path("map/<int:pk>", CHWLocationMapView.as_view(), name="chw_list_map"),
    path("chw/map/<int:pk>", CHWLocationMapView.as_view(), name="chw_map"),
    path("api/", include(router.urls)),
    path(
        "chw/<int:district_pk>/<int:slug>",
        CHWTargetAreaMapView.as_view(),
        name="target_area_map",
    ),
    path("performance/", include(performance_urls, namespace="performance")),
]
