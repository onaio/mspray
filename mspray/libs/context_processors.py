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
    }
