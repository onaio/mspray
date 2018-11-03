# -*- coding: utf-8 -*-
"""
alerts.urls module.
"""
from django.urls import path

from mspray.apps.alerts.views import (
    start_health_facility_catchment,
    start_send_weekly_update_email,
    start_so_daily_form_completion,
    daily_spray_effectiveness,
)

app_name = "alerts"  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    path(
        "health-facility-catchment/",
        start_health_facility_catchment,
        name="health_facility_catchment",
    ),
    path(
        "so-daily-form-completion/",
        start_so_daily_form_completion,
        name="so_daily_form_completion",
    ),
    path(
        "weekly-update-email/",
        start_send_weekly_update_email,
        name="send_weekly_update_email",
    ),
    path(
        "daily-spray-effectiveness",
        daily_spray_effectiveness,
        name="daily_spray_effectiveness",
    ),
]
