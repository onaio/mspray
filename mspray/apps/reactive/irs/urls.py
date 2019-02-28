"""urls module for Reactive IRS"""
from django.urls import path

from mspray.apps.reactive.irs.views import CHWLocationMapView

# pylint: disable=invalid-name
app_name = "reactive_irs"
urlpatterns = [
    path("chw/<int:pk>", CHWLocationMapView.as_view(), name="chw_location")
]
