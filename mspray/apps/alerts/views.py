# -*- coding: utf-8 -*-
"""Views that trigger notifications or alerts via RapidPro."""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.timezone import now
from django.conf import settings

from mspray.apps.alerts.tasks import (
    health_facility_catchment_hook,
    so_daily_form_completion,
    task_send_weekly_update_email,
    daily_spray_effectiveness_task,
)


@api_view(["GET", "POST"])
def start_health_facility_catchment(request):
    """Trigger the Health Facility Catchment notification."""
    health_facility_catchment_hook.delay()
    return Response({"success": True})


@api_view(["GET", "POST"])
def start_send_weekly_update_email(request):
    """Trigger weekly email."""
    task_send_weekly_update_email.delay()
    return Response({"success": True})


@api_view(["GET", "POST"])
def start_so_daily_form_completion(request):
    """Trigger spray operator daily form completion notification."""
    if request.method == "POST":
        district_code = request.data.get("district")
        tla_code = request.data.get("SO_name")
        confirmdecision = request.data.get("confirmdecisionform")
        so_daily_form_completion.delay(
            district_code, tla_code, confirmdecision
        )
    return Response({"success": True})


@api_view(["GET", "POST"])
def daily_spray_effectiveness(request):
    """Trigger spray area spray effectiveness notification."""
    flow_uuid = getattr(settings, "RAPIDPRO_DAILY_SPRAY_SUCCESS_FLOW_ID")
    spray_date = request._request.GET.get("spray_date", now().date())
    daily_spray_effectiveness_task.delay(flow_uuid, spray_date)

    return Response({"success": True})
