import os
from mspray.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'zambia',
        'USER': 'zambia',
        'PASSWORD': 'mspray',
        'HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', '127.0.0.1'),
    }
}

NOSE_ARGS = ['--stop']
NOSE_PLUGINS = ['mspray.libs.utils.nose_plugins.SilenceSouth']

SITE_NAME = DATABASES['default']['NAME']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': SITE_NAME,
    }
}
BUFFER_TOLERANCE = 0  # 0.0000021

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    'mspray.onalabs.org',
    'api.mspray.onalabs.org',
    'localhost:3000'
)

HH_BUFFER = True
DEBUG = True
ALLOWED_HOSTS = (
    'localhost',
)

BROKER_URL = 'amqp://{}:{}@localhost//{}'.format(
    SITE_NAME, SITE_NAME, SITE_NAME
)

# CELERY_ALWAYS_EAGER = True
ONA_API_TOKEN = '2cbfec2b6a74fc56f4326f2ca111544d8a9cb0d2'

# namibia
# DATABASES['default']['NAME'] = 'namibia'
# SITE_NAME = DATABASES['default']['NAME']
# MSPRAY_LOCATION_FIELD = 'target_area'
# MSPRAY_STRUCTURE_GPS_FIELD = 'structuredetails/homestead_gps'
# HAS_SPRAYABLE_QUESTION = True
# MSPRAY_SPATIAL_QUERIES = True
# namibia

# madagascar
# MSPRAY_LOCATION_FIELD = 'fokontany'
# MSPRAY_SPATIAL_QUERIES = False
# MSPRAY_WAS_SPRAYED_FIELD = 'was_sprayed'
# MSPRAY_WAS_SPRAYED_FIELD = 'sprayable/was_sprayed'
# MSPRAY_UNSPRAYED_REASON_FIELD = "sprayable/unsprayed/reason"
# MSPRAY_IRS_NUM_FIELD = 'irs_card_num'
# MSPRAY_UNSPRAYED_REASON_REFUSED = "2"
# MSPRAY_UNSPRAYED_REASON_OTHER = {
#     "1": "Locked",
#     "3": "Sick",
#     "4": "Family Event",
#     "5": "Other"
# }


# MSPRAY_STRUCTURE_GPS_FIELD = 'structure_gps'
# MSPRAY_SPRAY_OPERATOR_NAME = 'sprayop_name'
# MSPRAY_SPRAY_OPERATOR_CODE = 'sprayop_code'
# MSPRAY_SPRAY_OPERATOR_NAME = 'sprayable/sprayop_name'
# MSPRAY_SPRAY_OPERATOR_CODE = 'sprayable/sprayop_code'
# MSPRAY_TA_LEVEL = 'fokontany'

# MSPRAY_WAS_SPRAYED_FIELD = 'sprayable/was_sprayed'
# MSPRAY_UNSPRAYED_REASON_OTHER = {
#     "S": "Sick",
#     "L": "Locked",
#     "F": "Funeral",
#     "R": "Refused",
#     "M": "No one home/Missed",
#     "O": "Other"
# }
# HAS_SPRAYABLE_QUESTION = True
# MSPRAY_SPATIAL_QUERIES = False

# zambia
# DATABASES['default']['NAME'] = 'zambia'
OSM_SUBMISSIONS = True

MSPRAY_WAS_SPRAYED_FIELD = 'sprayable/was_sprayed'
MSPRAY_UNSPRAYED_REASON_FIELD = "sprayable/unsprayed/reason"
MSPRAY_UNSPRAYED_REASON_OTHER = {
    "S": "Sick",
    "L": "Locked",
    "F": "Funeral",
    "R": "Refused",
    "M": "No one home/Missed",
    "O": "Other"
}
MSPRAY_UNSPRAYED_REASON_REFUSED = "R"
MSPRAY_SPRAY_OPERATOR_NAME = 'sprayable/sprayop_name'
MSPRAY_SPRAY_OPERATOR_CODE = 'sprayable/sprayop_code'
MSPRAY_TEAM_LEADER_NAME = 'team_leader'
MSPRAY_TEAM_LEADER_CODE = 'team_code'
MSPRAY_IRS_NUM_FIELD = 'sprayable/irs_card_num'
HAS_SPRAYABLE_QUESTION = True
MSPRAY_SPATIAL_QUERIES = False
MSPRAY_UNIQUE_FIELD = 'osmstructure'
MSPRAY_STRUCTURE_GPS_FIELD = 'newstructure/gps'
MSPRAY_LOCATION_FIELD = 'target_area'
# zambia
