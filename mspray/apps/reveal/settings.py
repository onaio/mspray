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
