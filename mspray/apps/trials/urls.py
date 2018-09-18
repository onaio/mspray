# -*- coding: utf-8 -*-
"""Trials urls"""
from django.urls import path

from mspray.apps.trials import views

app_name = "trials"  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path("", views.index, name="index"),
    path("<int:site_id>", views.site, name="site"),
    path("<int:slug>)/map", views.SiteMapView.as_view(), name="site-map"),
]
