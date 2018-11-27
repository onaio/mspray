# -*- coding: utf-8 -*-
"""context processors.
"""
from django.conf import settings


def google_settings(request):
    """Set GOOGLE_API_KEY"""
    return {"GOOGLE_API_KEY": getattr(settings, "GOOGLE_API_KEY", "")}


def mspray_settings(request):
    """Set WAS_SPRAYED_VALUE and WAS_NOT_SPRAYED_VALUE"""
    return {
        "WAS_SPRAYED_VALUE": getattr(
            settings, "MSPRAY_WAS_SPRAYED_VALUE", "yes"
        ),
        "WAS_NOT_SPRAYED_VALUE": getattr(
            settings, "MSPRAY_WAS_NOT_SPRAYED_VALUE", "no"
        ),
        "WAS_SPRAYED_VALUES": getattr(settings, "SPRAYED_VALUES", ["sprayed"]),
        "WAS_NOT_SPRAYED_VALUES": getattr(
            settings, "NOT_SPRAYED_VALUES", ["notsprayed"]
        ),
    }


def show_directly_observed(request):
    """Set SHOW_DIRECTLY_OBSERVED context variable

    If true the Directly Observed Spraying link will be displayed.
    """
    return {
        "SHOW_DIRECTLY_OBSERVED": getattr(
            settings, "SHOW_DIRECTLY_OBSERVED", False
        )
    }


def show_trial_survey(request):
    """Set SHOW_TRIAL_SURVEY context variable

    If true the Trial Survey link will be displayed.
    """
    return {"SHOW_TRIAL_SURVEY": getattr(settings, "SHOW_TRIAL_SURVEY", False)}


def enable_mda(request):
    """Set ENABLE_MDA context variable

    When ENABLE_MDA is set to True the MDA dashboard links are enabled.
    """
    return {
        "ENABLE_MDA": getattr(settings, "ENABLE_MDA", False),
        "MDA_STATIC_PREFIX": getattr(settings, "MDA_STATIC_PREFIX", "/mda"),
    }


def community_health_worker(request):
    """Set COMMUNITY HEALTH WORKER value."""
    return {
        "COMMUNITY_HEALTH_WORKER": getattr(
            settings,
            "MSPRAY_COMMUNITY_HEALTH_WORKER", "community health worker")}


def supervisor(request):
    """Set SUPERVISOR value."""
    return {
        "SUPERVISOR": getattr(settings, "MSPRAY_SUPERVISOR", "supervisor")}
