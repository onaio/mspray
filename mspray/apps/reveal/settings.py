"""settings for reveal app"""
from django.conf import settings

ENABLE_REVEAL = getattr(settings, "ENABLE_REVEAL", False)
REVEAL_LABEL = getattr(settings, "REVEAL_LABEL", "Reveal")
REVEAL_SPRAY_STATUS_FIELD = getattr(settings, "REVEAL_SPRAY_STATUS_FIELD",
                                    "task_business_status")
REVEAL_SPRAYED_VALUE = getattr(settings, "REVEAL_SPRAYED_VALUE", "Sprayed")
REVEAL_NOT_SPRAYED_VALUE = getattr(settings, "REVEAL_NOT_SPRAYED_VALUE",
                                   "Not Sprayed")
REVEAL_NOT_VISITED_VALUE = getattr(settings, "REVEAL_NOT_VISITED_VALUE",
                                   "Not Visited")
REVEAL_NOT_SPRAYABLE_VALUE = getattr(settings, "REVEAL_NOT_SPRAYABLE_VALUE",
                                     "Not Sprayable")
REVEAL_DATA_ID_FIELD = getattr(settings, "REVEAL_DATA_ID_FIELD", "task_id")
REVEAL_DATE_FIELD = getattr(settings, "REVEAL_DATE_FIELD",
                            "task_execution_start_date")
REVEAL_GPS_FIELD = getattr(settings, "REVEAL_GPS_FIELD", "geometry")
REVEAL_OSMNODE_FIELD = getattr(settings, "REVEAL_OSMNODE_FIELD",
                               "osmstructure:node:id")
REVEAL_NEWSTRUCTURE_GPS_FIELD = getattr(
    settings, "REVEAL_NEWSTRUCTURE_GPS_FIELD", "newstructure/gps")
REVEAL_OPENSRP_USERNAME = getattr(settings, "REVEAL_OPENSRP_USERNAME", "")
REVEAL_OPENSRP_PASSWORD = getattr(settings, "REVEAL_OPENSRP_PASSWORD", "")
REVEAL_OPENSRP_BASE_URL = getattr(
    settings,
    "REVEAL_OPENSRP_BASE_URL",
    "https://reveal-stage.smartregister.org/opensrp/rest/",
)
REVEAL_OPENSRP_CREATE_PARENT_LOCATIONS_ENDPOINT = getattr(
    settings,
    "REVEAL_OPENSRP_CREATE_PARENT_LOCATIONS_ENDPOINT",
    "location/add?is_jurisdiction=true",
)
REVEAL_OPENSRP_CREATE_STRUCTURE_LOCATIONS_ENDPOINT = getattr(
    settings, "REVEAL_OPENSRP_CREATE_STRUCTURE_LOCATIONS_ENDPOINT",
    "location/add")
REVEAL_OPENSRP_ACTIVE = getattr(settings, "REVEAL_OPENSRP_ACTIVE", "Active")
REVEAL_DISTRICT = getattr(settings, "REVEAL_DISTRICT", "district")
REVEAL_OPENSRP_DISTRICT = getattr(settings, "REVEAL_OPENSRP_DISTRICT", 0)
REVEAL_RHC = getattr(settings, "REVEAL_RHC", "RHC")
REVEAL_OPENSRP_RHC = getattr(settings, "REVEAL_OPENSRP_RHC", 1)
REVEAL_TARGET_AREA = getattr(settings, "REVEAL_TARGET_AREA", "ta")
REVEAL_OPENSRP_TARGET_AREA = getattr(settings, "REVEAL_OPENSRP_TARGET_AREA", 2)
REVEAL_OPENSRP_HOUSEHOLD = getattr(settings, "REVEAL_OPENSRP_HOUSEHOLD", 4)
REVEAL_SPRAY_OPERATOR = getattr(settings, "REVEAL_SPRAY_OPERATOR",
                                "task_spray_operator")

# these general mSpray fields should be set up this way
# this is commented out so that it does not affect other mSpray tests
# MSPRAY_OSM_PRESENCE_FIELD = False
# SPRAYABLE_FIELD = REVEAL_SPRAY_STATUS_FIELD
# MSPRAY_WAS_SPRAYED_FIELD = REVEAL_SPRAY_STATUS_FIELD
# NOT_SPRAYABLE_VALUE = REVEAL_NOT_SPRAYABLE_VALUE
# SPRAYED_VALUE = REVEAL_SPRAYED_VALUE
# SPRAYED_VALUES = [REVEAL_SPRAYED_VALUE]
# MSPRAY_DATE_FIELD = REVEAL_DATE_FIELD
# MSPRAY_WAS_SPRAYED_VALUE = REVEAL_SPRAYED_VALUE
# MSPRAY_WAS_NOT_SPRAYED_VALUE = REVEAL_NOT_SPRAYED_VALUE
# MSPRAY_SPRAY_OPERATOR_NAME = REVEAL_SPRAY_OPERATOR
# MSPRAY_SPRAY_OPERATOR_CODE = REVEAL_SPRAY_OPERATOR
