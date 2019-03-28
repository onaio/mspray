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
from mspray.apps.reactive.irs.views import (CHWDistrictsView, CHWListView,
                                            CHWLocationMapView)

router = routers.DefaultRouter(trailing_slash=False)  # pylint: disable=C0103

router.register(r"buffers", household_buffer.HouseholdBufferViewSet)
router.register(r"districts", districts.DistrictViewSet, "district")
router.register(r"households", household.HouseholdViewSet)
router.register(r"spraydays", sprayday.SprayDayViewSet)
router.register(r"targetareas", target_area.TargetAreaViewSet)

# pylint: disable=invalid-name
app_name = "reactive_irs"
urlpatterns = [
    path("", CHWDistrictsView.as_view(), name="district_list"),
    path("<int:pk>", CHWListView.as_view(), name="chw_list"),
    path("map/<int:pk>", CHWLocationMapView.as_view(), name="chw_list_map"),
    path("chw/map/<int:pk>", CHWLocationMapView.as_view(), name="chw_map"),
    path("api/", include(router.urls)),
]
