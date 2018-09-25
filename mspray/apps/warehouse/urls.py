# -*- coding: utf-8 -*-
"""
warehouse.urls module.
"""
from django.urls import path

from mspray.apps.warehouse.views import (AllTargetAreas, DistrictMap,
                                         DistrictView, Home, RHCMap, RHCView,
                                         TargetAreaMap)

app_name = "warehouse"  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path("home/", Home.as_view(), name="home"),
    path("district/<int:pk>/", DistrictView.as_view(), name="district"),
    path("rhc/<int:pk>/", RHCView.as_view(), name="rhc"),
    path("target-area/map/<int:pk>/", TargetAreaMap.as_view(), name="ta"),
    path("rhc/map/<int:pk>/", RHCMap.as_view(), name="rhc_map"),
    path("district/map/<int:pk>/", DistrictMap.as_view(), name="district_map"),
    path(
        "spray-effectiveness/spray-areas/",
        AllTargetAreas.as_view(),
        name="spray_areas",
    ),
]
