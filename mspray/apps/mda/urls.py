# -*- coding: utf-8 -*-
"""MDA urls"""
from django.urls import path

from mspray.apps.mda.views.index import MDALocationView, MDAView
from mspray.apps.mda.views.map import MapView

app_name = "mda"  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path("", MDAView.as_view(), name="index"),
    path("<int:location>", MDALocationView.as_view(), name="location"),
    path("<int:district_pk>/<int:slug>", MapView.as_view(), name="spray-area"),
]
