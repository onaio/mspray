"""urls module for Reactive IRS"""
from django.urls import path

from mspray.apps.reactive.irs.views import CHWLocationMapView, CHWListView

# pylint: disable=invalid-name
app_name = "reactive_irs"
urlpatterns = [
    path("<int:pk>", CHWListView.as_view(), name="chw_list"),
    path("chw/<int:pk>", CHWLocationMapView.as_view(), name="chw_map")
]
