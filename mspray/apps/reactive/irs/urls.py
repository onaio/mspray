"""urls module for Reactive IRS"""
from django.urls import path

from mspray.apps.reactive.irs.views import CHWListView, CHWLocationMapView

# pylint: disable=invalid-name
app_name = "reactive_irs"
urlpatterns = [
    path("<int:pk>", CHWListView.as_view(), name="chw_list"),
    path("map/<int:pk>", CHWLocationMapView.as_view(), name="chw_list_map"),
    path("chw/map/<int:pk>", CHWLocationMapView.as_view(), name="chw_map"),
]
