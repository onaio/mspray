# -*- coding: utf-8 -*-
"""
Django settings for mspray project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

from django.core.exceptions import SuspiciousOperation


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "mspray.libs.context_processors.google_settings",
                "mspray.libs.context_processors.mspray_settings",
                "mspray.libs.context_processors.show_directly_observed",
                "mspray.libs.context_processors.show_trial_survey",
            ],
            "debug": False,
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    }
]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "u3rh4x=!%7j4@e4*ctww1v+rt4614%kgiow(k@74qsl0-s6yn^"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.humanize",
    "django.contrib.postgres",
    "corsheaders",
    "django_nose",
    "rest_framework",
    "rest_framework_gis",
    "storages",
    "mspray.apps.main",
    "mspray.apps.warehouse",
    "mspray.apps.alerts",
    "mspray.apps.trials",
)

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "mspray.urls"

WSGI_APPLICATION = "mspray.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        'NAME': os.environ.get('DB_NAME', 'mspray'),
        "USER": os.environ.get('DB_USER', 'mspray'),
        "PASSWORD": os.environ.get('DB_PASS', 'mspray'),
        "HOST": os.environ.get('DB_HOST', '127.0.0.1'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = "/static/"

# nose
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

NOSE_ARGS = [
    "--with-coverage",
    "--cover-package=mspray",
    "--with-fixture-bundling",
    "--nologcapture",
    "--nocapture",
]

CORS_ORIGIN_ALLOW_ALL = True
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "static"))
POSTGIS_VERSION = (2, 1, 1)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

BUFFER_TOLERANCE = 0.0000021

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "mspray.libs.renderers.GeoJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    )
}


def skip_suspicious_operations(record):
    """Prevent django from sending 500 error
    email notifications for SuspiciousOperation
    events, since they are not true server errors,
    especially when related to the ALLOWED_HOSTS
    configuration

    background and more information:
    http://www.tiwoc.de/blog/2013/03/django-prevent-email-notification-on-susp\
    iciousoperation/
    """
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, SuspiciousOperation):
            return False
    return True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "%(levelname)s %(asctime)s %(module)s"
                " %(process)d %(thread)d %(message)s"
            )
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        # Define filter for suspicious urls
        "skip_suspicious_operations": {
            "()": "django.utils.log.CallbackFilter",
            "callback": skip_suspicious_operations,
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false", "skip_suspicious_operations"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "console_logger": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

MSPRAY_EMAIL = "mspray@example.com"
MSPRAY_REPLY_TO_EMAIL = "mspray@example.com"
MSPRAY_LOCATION_FIELD = "location_code"
MSPRAY_WAS_SPRAYED_FIELD = "sprayed/was_sprayed"
MSPRAY_NEW_STRUCTURE_WAS_SPRAYED_FIELD = "sprayed/was_sprayed"
MSPRAY_WAS_SPRAYED_VALUE = "yes"
MSPRAY_WAS_NOT_SPRAYED_VALUE = "no"
SPRAYABLE_FIELD = "sprayable_structure"
NOT_SPRAYABLE_VALUE = "no"
MSPRAY_SPATIAL_QUERIES = True
MSPRAY_UNSPRAYED_REASON_FIELD = "unsprayed/reason"
MSPRAY_UNSPRAYED_REASON_REFUSED = "Refused"
MSPRAY_UNSPRAYED_REASON_OTHER = {
    "Other": "Other",
    "Sick": "Sick",
    "Funeral": "Funeral",
    "Locked": "Locked",
    "No one home/Missed": "No one home/Missed",
}
MSPRAY_OSM_PRESENCE_FIELD = "osmstructure:spray_status"
MSPRAY_USER_LATLNG_FIELD = "osmstructure:userlatlng"
MPSRAY_DATA_FILTER = '"sprayable_structure":"yes"'
MSPRAY_DATA_ID_FIELD = "_id"
MSPRAY_DATE_FIELD = "today"
MSPRAY_STRUCTURE_GPS_FIELD = "structuredetails/structure_gps"
MPSRYA_NON_STRUCTURE_GPS_FIELD = "non_structure_gps"
MSPRAY_SPRAY_OPERATOR_NAME = "sprayed/sprayop_name"
MSPRAY_SPRAY_OPERATOR_CODE = "sprayed/sprayop_code"
MSPRAY_TEAM_LEADER_NAME = "team_leader"
MSPRAY_TEAM_LEADER_CODE = "team_leader"
MSPRAY_TEAM_LEADER_ASSISTANT_NAME = "team_leader_assistant"
MSPRAY_TEAM_LEADER_ASSISTANT_CODE = "team_leader_assistant"
MSPRAY_TA_LEVEL = "ta"
MSPRAY_IRS_NUM_FIELD = "irs_sticker_num"
HIGHER_LEVEL_MAP = True
HH_BUFFER = False
HEALTH_FACILITY_CATCHMENT_THRESHOLD = 10
ONA_URI = "https://ona.io"
MSPRAY_WEEKLY_DASHBOARD_UPDATE_URL = "http://example.com"
MSPRAY_AWS_PATH = "mspray"

BROKER_URL = "amqp://guest:guest@localhost//"
OSM_SUBMISSIONS = False
HAS_SPRAYABLE_QUESTION = False
SITE_NAME = "mSpray"
SPRAYABLE_FIELD = "sprayable_structure"
NEW_STRUCTURE_SPRAYABLE_FIELD = "sprayable_structure"
NOT_SPRAYABLE_VALUE = "no"
LOCATION_SPRAYED_PERCENTAGE = 90
FALLBACK_TO_SUBMISSION_DATA_LOCATION = False

DRUID_BROKER_URI = "http://127.0.0.1"
DRUID_BROKER_PORT = 8082
DRUID_OVERLORD_URI = "http://127.0.0.1"
DRUID_OVERLORD_PORT = 8090
DRUID_SPRAYDAY_TRANQUILITY_URI = "http://127.0.0.1"
DRUID_SPRAYDAY_TRANQUILITY_PORT = 8200
DRUID_SPRAYDAY_TRANQUILITY_PATH = "/v1/post/mspray"
DRUID_SPRAYDAY_DATASOURCE = "mspray"
DRUID_HOUSEHOLD_DATASOURCE = "household"
DRUID_INTERVAL = "1917-09-08T00:00:00+00:00/2018-09-08T10:41:37+00:00"
DRUID_USE_INDEX_HADOOP = True
DRUID_TIMESTAMP_COLUMN = "timestamp"
DRUID_BATCH_PROCESS_TIME_INTERVAL = 5  # minutes

RAPIDPRO_API_TOKEN = "api_token"
RAPIDPRO_API_URL = "rapidpro.ona.io"
RAPIDPRO_DEFAULT_CONTACT_ID = ""
RAPIDPRO_DAILY_SPRAY_SUCCESS_FLOW_ID = ""
RAPIDPRO_DAILY_FOUND_COVERAGE_FLOW_ID = ""
RAPIDPRO_USER_DISTANCE_FLOW_ID = ""
RAPIDPRO_NO_GPS_FLOW_ID = ""
RAPIDPRO_SO_DAILY_COMPLETION_FLOW_ID = ""
RAPIDPRO_NO_REVISIT_FLOW_ID = ""
RAPIDPRO_HF_CATCHMENT_FLOW_ID = ""
RAPIDPRO_WEEKLY_UPDATE_CONTACT_GROUP = ""

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
