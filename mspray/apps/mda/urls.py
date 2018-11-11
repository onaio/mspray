# -*- coding: utf-8 -*-
"""MDA urls"""
from django.conf.urls import include
from django.urls import path

from mspray.apps.main.views import performance
from mspray.apps.mda.views.index import MDALocationView, MDAView
from mspray.apps.mda.views.map import MapView

app_name = "mda"  # pylint: disable=invalid-name

performance_urls = (  # pylint: disable=C0103
    [
        path(
            "", performance.DistrictPerfomanceView.as_view(), name="districts"
        ),
        path(
            "team-leaders/<int:slug>",
            performance.TeamLeadersPerformanceView.as_view(),
            name="team-leaders",
        ),
        path(
            "spray-operators/<int:slug>/<int:team_leader>/summary",
            performance.SprayOperatorSummaryView.as_view(),
            name="spray-operator-summary",
        ),
        path(
            "spray-operators/<int:slug>/<int:team_leader>/"
            "<int:spray_operator>/daily",
            performance.SprayOperatorDailyView.as_view(),
            name="spray-operator-daily",
        ),
        path(
            "definitions-and-conditions",
            performance.DefinitionAndConditionView.as_view(),
            name="definitions-and-conditions",
        ),
    ],
    "mspray",
)

urlpatterns = [  # pylint: disable=invalid-name
    path("", MDAView.as_view(), name="index"),
    path("<int:location>", MDALocationView.as_view(), name="location"),
    path("<int:district_pk>/<int:slug>", MapView.as_view(), name="spray-area"),
    path("performance", include(performance_urls, namespace="performance")),
]
