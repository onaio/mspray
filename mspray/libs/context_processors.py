from django.conf import settings


def google_settings(request):
    return {
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY
    }


def mspray_settings(request):
    return {
        'WAS_SPRAYED_VALUE':
        getattr(settings, 'MSPRAY_WAS_SPRAYED_VALUE', 'yes'),
        'WAS_NOT_SPRAYED_VALUE':
        getattr(settings, 'MSPRAY_WAS_NOT_SPRAYED_VALUE', 'no')
    }
