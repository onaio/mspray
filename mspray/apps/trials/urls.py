# -*- coding: utf-8 -*-
"""Trials urls"""
from django.conf.urls import url

from mspray.apps.trials import views

urlpatterns = [  # pylint: disable=invalid-name
    url('^$', views.index, name='index'),
    url('(?P<site_id>[0-9]+)$', views.site, name='site'),
    # url('(?P<site_id>[0-9]+)/map$', views.site_map, name='site-map'),
    url(r'^(?P<slug>\d+)/map$', views.SiteMapView.as_view(), name='site-map'),
]
