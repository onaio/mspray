from mspray.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'REPLACE_DB_NAME',
        'USER': 'REPLACE_DB_USER',
        'PASSWORD': 'REPLACE_DB_PASSWORD',
        'HOST': 'REPLACE_DB_HOST',
    }
}

NOSE_ARGS = ['--stop']
NOSE_PLUGINS = ['mspray.libs.utils.nose_plugins.SilenceSouth']
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'static'))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    'PROJECT.mspray.onalabs.org',
    'PROJECT.api.mspray.onalabs.org',
    'localhost:3000'
)

SITE_NAME = 'PROJECT'

MSPRAY_LOCATION_FIELD = 'fokontany'
MSPRAY_SPATIAL_QUERIES = False
MSPRAY_WAS_SPRAYED_FIELD = 'was_sprayed'
MSPRAY_UNSPRAYED_REASON_REFUSED = "2"
MSPRAY_UNSPRAYED_REASON_OTHER = {
    "1": "Locked",
    "3": "Sick",
    "4": "Family Event",
    "5": "Other"
}

MSPRAY_STRUCTURE_GPS_FIELD = 'structure_gps'
MSPRAY_SPRAY_OPERATOR_NAME = 'sprayop_name'
MSPRAY_SPRAY_OPERATOR_CODE = 'sprayop_code'
