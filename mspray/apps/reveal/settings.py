"""settings for reveal app"""
from django.conf import settings

REVEAL_DATA_ID_FIELD = getattr(settings, "REVEAL_DATA_ID_FIELD", "id")
REVEAL_DATE_FIELD = getattr(settings, "REVEAL_DATE_FIELD", "date")
REVEAL_GPS_FIELD = getattr(settings, "REVEAL_GPS_FIELD", "location")
REVEAL_OPENSRP_USERNAME = getattr(settings, "REVEAL_OPENSRP_USERNAME", "")
REVEAL_OPENSRP_PASSWORD = getattr(settings, "REVEAL_OPENSRP_PASSWORD", "")
REVEAL_OPENSRP_BASE_URL = getattr(
    settings, "REVEAL_OPENSRP_BASE_URL",
    "https://reveal-stage.smartregister.org/opensrp/rest/")
REVEAL_OPENSRP_CREATE_PARENT_LOCATIONS_ENDPOINT = getattr(
    settings, "REVEAL_OPENSRP_CREATE_PARENT_LOCATIONS_ENDPOINT",
    "/location/add?is_jurisdiction=true"
)
REVEAL_OPENSRP_CREATE_STRUCTURE_LOCATIONS_ENDPOINT = getattr(
    settings, "REVEAL_OPENSRP_CREATE_STRUCTURE_LOCATIONS_ENDPOINT",
    "/location/add")
REVEAL_OPENSRP_ACTIVE = getattr(settings, "REVEAL_OPENSRP_ACTIVE", "Active")
REVEAL_DISTRICT = getattr(settings, 'REVEAL_DISTRICT', "district")
REVEAL_OPENSRP_DISTRICT = getattr(settings, 'REVEAL_OPENSRP_DISTRICT', 0)
REVEAL_RHC = getattr(settings, 'REVEAL_RHC', "RHC")
REVEAL_OPENSRP_RHC = getattr(settings, 'REVEAL_OPENSRP_RHC', 1)
REVEAL_TARGET_AREA = getattr(settings, 'REVEAL_TARGET_AREA', "ta")
REVEAL_OPENSRP_TARGET_AREA = getattr(settings, 'REVEAL_OPENSRP_TARGET_AREA', 2)
REVEAL_OPENSRP_HOUSEHOLD = getattr(settings, 'REVEAL_OPENSRP_HOUSEHOLD', 4)
