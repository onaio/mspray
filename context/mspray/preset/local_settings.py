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
