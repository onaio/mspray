# -*- coding -*-
"""
mSpray settings module to use with the Dockerfile.
"""
import os

# pylint: disable=wildcard-import,unused-wildcard-import
from mspray.settings import *  # noqa

NOSE_ARGS = [
    "--cover-package=mspray",
    "--cover-erase",
    "--cover-inclusive",
    "--with-coverage",
    "--verbosity=2",
    "--with-fixture-bundling",
]
NOSE_PLUGINS = ["mspray.libs.utils.nose_plugins.SilenceSouth"]
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "static"))  # noqa

CORS_ORIGIN_ALLOW_ALL = False

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SECRET_KEY = "some random secret key"

OSM_SUBMISSIONS = True
HH_BUFFER = True
MSPRAY_NEW_BUFFER_WIDTH = 4

MSPRAY_WAS_SPRAYED_FIELD = "values_from_omk/spray_status"
MSPRAY_NEW_STRUCTURE_WAS_SPRAYED_FIELD = "newstructure/manual_spray_status"
MSPRAY_WAS_SPRAYED_VALUE = "sprayed"
MSPRAY_WAS_NOT_SPRAYED_VALUE = "notsprayed"
MSPRAY_UNSPRAYED_REASON_FIELD = "osmstructure:notsprayed_reason"
MSPRAY_UNSPRAYED_REASON_OTHER = {
    "sick": "Sick",
    "locked": "Locked",
    "funeral": "Funeral",
    "refused": "Refused",
    "no_one_home": "No one home/Missed",
    "other": "Other",
}

MSPRAY_UNSPRAYED_REASON_REFUSED = "refused"
MSPRAY_SPRAY_OPERATOR_NAME = "sprayable/sprayop_name"
MSPRAY_SPRAY_OPERATOR_CODE = "sprayable/sprayop_code"
MSPRAY_TEAM_LEADER_NAME = "tla_leader"
MSPRAY_TEAM_LEADER_CODE = "tl_code"
MSPRAY_TEAM_LEADER_ASSISTANT_CODE = "tla_leader"
MSPRAY_IRS_NUM_FIELD = "irs_card_num"
HAS_SPRAYABLE_QUESTION = True
MSPRAY_UNIQUE_FIELD = "osmstructure"
MSPRAY_STRUCTURE_GPS_FIELD = "newstructure/gps"

SPRAYABLE_FIELD = "values_from_omk/spray_status"
NEW_STRUCTURE_SPRAYABLE_FIELD = "newstructure/manual_spray_status"
NOT_SPRAYABLE_VALUE = "noteligible"
