# -*- coding: utf-8 -*-
"""MDA urls"""
from mspray.apps.mda.views.index import MDAView, MDALocationView
from django.urls import path

app_name = "mda"  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path("", MDAView.as_view(), name="index"),
    path("<int:location>", MDALocationView.as_view(), name="location"),
]
