# -*- coding: utf-8 -*-
"""
Mspray urls module.
"""
import sys

from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin
from django.urls import path

from rest_framework import routers

from mspray.apps.alerts import urls as alerts_urls
from mspray.apps.main.views import directly_observed_spraying_form as dos_form
from mspray.apps.main.views import (
    districts, home, household, household_buffer, indicators, performance,
    spray_operator_daily, sprayday, target_area, user)
from mspray.apps.main.views.decision import DecisionView
from mspray.apps.main.views.mobilisation import MobilisationView
from mspray.apps.main.views.mopup import HealthFacilityMopUpView, MopUpView
from mspray.apps.main.views.sensitization_visit import SensitizationVisitView
from mspray.apps.main.views.sprayday import NoLocationSprayDayView
from mspray.apps.mda import urls as mda_urls
from mspray.apps.reactive.irs import urls as reactive_irs_urls
from mspray.apps.warehouse import urls as warehouse_urls

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

admin.autodiscover()

router = routers.DefaultRouter(trailing_slash=False)  # pylint: disable=C0103

router.register(r"buffers", household_buffer.HouseholdBufferViewSet)
router.register(r"districts", districts.DistrictViewSet, "district")
router.register(r"households", household.HouseholdViewSet)
router.register(r"spraydays", sprayday.SprayDayViewSet)
router.register(r"targetareas", target_area.TargetAreaViewSet)

performance_urls = (  # pylint: disable=C0103
    [
        path(
            "", performance.DistrictPerfomanceView.as_view(),
            name="districts"),
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
    path("reactive/irs/", include(reactive_irs_urls,
                                  namespace="reactive_irs")),
    path("mda/", include(mda_urls, namespace="mda")),
    path("mda-round-2/", include(mda_urls, namespace="mda-2")),
    path("trials/", include("mspray.apps.trials.urls", namespace="trials")),
    path("api/alerts/", include(alerts_urls, namespace="alerts")),
    path("api/", include(router.urls)),
    path("", home.DistrictView.as_view(), name="index"),
    path("login", user.login, name="login"),
    path("logout", user.logout, name="logout"),
    path(
        "not-in-target-area/",
        NoLocationSprayDayView.as_view(),
        name="no_location_spray_effectiveness",
    ),
    path("warehouse/", include(warehouse_urls, namespace="warehouse")),
    path(r"<int:pk>", home.DistrictView.as_view(), name="district"),
    path(
        "<int:district_pk>/<int:slug>",
        home.TargetAreaView.as_view(),
        name="target_area",
    ),
    path("sprayareas", home.SprayAreaView.as_view(), name="sprayareas"),
    path(
        "detailed-sprayareas/",
        home.DetailedCSVView.as_view(),
        name="detailed_sprayareas",
    ),
    path(
        "weekly-report", home.WeeklyReportView.as_view(),
        name="weeklyreports"),
    path(
        "indicators/number_of_households",
        indicators.NumberOfHouseholdsIndicatorView.as_view(),
        name="number_of_housesholds",
    ),
    path("performance/", include(performance_urls, namespace="performance")),
    path("reveal/", include("mspray.apps.reveal.urls", namespace="reveal")),
    path("admin/", admin.site.urls),
    path(
        "spray-operator-daily",
        spray_operator_daily.SprayOperatorDailyViewSet.as_view({
            "post": "create"
        }),
        name="spray-operator-daily",
    ),
    path(
        "directly-observed-spraying-form",
        dos_form.DirectlyObservedSprayingFormViewSet.as_view({
            "post": "create"
        }),
        name="directly-observed-spraying-form",
    ),
    path(
        "directly-observed-spraying",
        dos_form.DirectlyObservedSprayingView.as_view(),
        name="directly-observed-spraying",
    ),
    path(
        "directly-observed-spraying/<int:district>",
        dos_form.DirectlyObservedSprayingView.as_view(),
        name="dos-district",
    ),
    path(
        "directly-observed-spraying/<int:district>/<int:team_leader>",
        dos_form.DirectlyObservedSprayingView.as_view(),
        name="dos-team-leader",
    ),
    path(
        "directly-observed-spraying/<int:district>/<int:team_leader>/"
        "<int:spray_operator>",
        dos_form.DirectlyObservedSprayingView.as_view(),
        name="dos-spray-operator",
    ),
    path(
        "sensitization-visit",
        SensitizationVisitView.as_view(),
        name="sensitization-visit",
    ),
    path(
        "mobilisation-visit",
        MobilisationView.as_view(),
        name="mobilisation-visit"),
    path("decision-visit", DecisionView.as_view(), name="decision-visit"),
    path("mop-up", MopUpView.as_view(), name="mop-up"),
    path(
        "mop-up/<int:district>",
        HealthFacilityMopUpView.as_view(),
        name="mop-up"),
] + static.static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if (settings.DEBUG or TESTING) and "debug_toolbar" in settings.INSTALLED_APPS:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]
