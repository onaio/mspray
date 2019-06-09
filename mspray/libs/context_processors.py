# -*- coding: utf-8 -*-
"""
The mspray context processors.
"""
from django.conf import settings


def google_settings(request):
    """Set GOOGLE_API_KEY"""
    return {"GOOGLE_API_KEY": getattr(settings, "GOOGLE_API_KEY", "")}


def mspray_settings(request):
    """Set WAS_SPRAYED_VALUE and WAS_NOT_SPRAYED_VALUE"""
    return {
        "WAS_SPRAYED_VALUE": getattr(settings, "MSPRAY_WAS_SPRAYED_VALUE", "yes"),
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
        "SHOW_DIRECTLY_OBSERVED": getattr(settings, "SHOW_DIRECTLY_OBSERVED", False)
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
    url_path = request.get_full_path()
    is_mda_one = "mda" in url_path and "mda-round-2" not in url_path
    is_mda_two = "mda-round-2" in url_path
    is_reactive_irs = "reactive/irs" in url_path
    spray_area_url = "target_area"
    performance_district_url = "performance:districts"
    performance_team_leader_url = "performance:team-leaders"
    performance_rhc_url = "performance:rhcs"
    spray_operator_daily_url = "performance:spray-operator-daily"
    mda_static_prefix = getattr(settings, "MDA_STATIC_PREFIX", "/mda")
    static_url_prefix = "".join([url_path, mda_static_prefix])
    mopup_url = "mop-up"
    if is_mda_one:
        spray_area_url = "mda:spray-area"
        performance_district_url = "mda:performance:districts"
        performance_team_leader_url = "mda:performance:spray-operator-summary"
        performance_rhc_url = "mda:performance:rhcs"
        spray_operator_daily_url = "mda:performance:spray-operator-daily"
        mopup_url = "mda:mop-up"
    if is_mda_two:
        spray_area_url = "mda-2:spray-area"
        performance_district_url = "mda-2:performance:districts"
        performance_team_leader_url = "mda-2:performance:spray-operator-summary"
        performance_rhc_url = "mda-2:performance:rhcs"
        spray_operator_daily_url = "mda-2:performance:spray-operator-daily"
        mopup_url = "mda-2:mop-up"
    if is_reactive_irs:
        spray_area_url = "reactive_irs:target_area_map"
        spray_operator_daily_url = "reactive_irs:performance:spray-operator-daily"
        performance_district_url = "reactive_irs:performance:districts"
        performance_team_leader_url = "reactive_irs:performance:team-leaders"

    return {
        "ENABLE_MDA": getattr(settings, "ENABLE_MDA", False),
        "ENABLE_REACTIVE_IRS": getattr(settings, "ENABLE_REACTIVE_IRS", False),
        "MDA_STATIC_PREFIX": mda_static_prefix,
        "MSPRAY_STATIC_URL_PREFIX": static_url_prefix,
        "IS_MDA_LINK": is_mda_one,
        "IS_MDA_2_LINK": is_mda_two,
        "IS_REACTIVE_IRS_LINK": is_reactive_irs,
        "SPRAY_AREA_URL": spray_area_url,
        "PERFORMANCE_DISTRICT_URL": performance_district_url,
        "PERFORMANCE_TL_URL": performance_team_leader_url,
        "PERFORMANCE_RHC_URL": performance_rhc_url,
        "PERFORMANCE_SO_URL": spray_operator_daily_url,
        "MOPUP_URL": mopup_url,
    }


def reveal(request):
    """Set Reveal context data"""
    return {"ENABLE_REVEAL": getattr(settings, "ENABLE_REVEAL", False)}


def labels(request):
    """Set COMMUNITY HEALTH WORKER value."""
    return {
        "COMMUNITY_HEALTH_WORKER_LABEL": getattr(
            settings, "MSPRAY_COMMUNITY_HEALTH_WORKER_LABEL", "Spray Operator"
        ),
        "COMMUNITY_HEALTH_WORKER_LABEL_PLURAL": getattr(
            settings, "MSPRAY_COMMUNITY_HEALTH_WORKER_LABEL_PLURAL", "Spray Operators"
        ),
        "SUPERVISOR_LABEL": getattr(
            settings, "MSPRAY_SUPERVISOR_LABEL", "Team Leader Assistant (TLA)"
        ),
        "SUPERVISOR_LABEL_PLURAL": getattr(
            settings, "MSPRAY_SUPERVISOR_LABEL_PLURAL", "Team Leader Assistants (TLA)"
        ),
        "RHC_LABEL": getattr(settings, "MSPRAY_RHC_LABEL", "RHC"),
        "RHC_LABEL_PLURAL": getattr(settings, "MSPRAY_RHC_LABEL_PLURAL", "RHCs"),
        "MDA_ROUND_ONE_LABEL": getattr(settings, "MSPRAY_MDA_ROUND_ONE", "MDA Round 1"),
        "MSPRAY_REACTIVE_IRS_LABEL": getattr(
            settings, "MSPRAY_REACTIVE_IRS", "Reactive IRS"
        ),
        "MDA_ROUND_TWO_LABEL": "MDA Round 2",
        "REVEAL_LABEL": getattr(settings, "REVEAL_LABEL", "Reveal"),
    }
