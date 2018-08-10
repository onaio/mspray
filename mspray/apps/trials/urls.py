# -*- coding: utf-8 -*-
"""Trials urls"""
from django.conf.urls import url

from mspray.apps.trials import views

urlpatterns = [  # pylint: disable=invalid-name
    url('^$', views.index, name='index'),
]
