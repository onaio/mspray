"""module to export reveal locations"""
from urllib.parse import urljoin

from django.conf import settings

import requests
from requests.auth import HTTPBasicAuth
from rest_framework.renderers import JSONRenderer

from mspray.apps.main.models import Household, Location
from mspray.apps.reveal.serializers import (HouseholdSerializer,
                                            LocationSerializer)


def send_request(
        url: str,
        payload: str,
        username: str = settings.REVEAL_OPENSRP_USERNAME,
        password: str = settings.REVEAL_OPENSRP_PASSWORD,
):
    """Send the POST request to OpenSRP"""
    auth = HTTPBasicAuth(username, password)
    request = requests.post(
        url,
        data=payload,
        auth=auth,
        headers={'Content-type': 'application/json'})

    return request.status_code in [200, 201]


def export_locations(queryset):
    """
    Export locations in bulk
    """
    url = urljoin(settings.REVEAL_OPENSRP_BASE_URL,
                  settings.REVEAL_OPENSRP_CREATE_PARENT_LOCATIONS_ENDPOINT)
    payload = []

    for item in queryset.iterator():
        serializer = LocationSerializer(item)
        payload.append(serializer.data)

    json_data = JSONRenderer().render(payload)

    res = send_request(url=url, payload=json_data)

    return res


def export_households(location):
    """
    Export households from one target area in bulk
    """
    url = urljoin(settings.REVEAL_OPENSRP_BASE_URL,
                  settings.REVEAL_OPENSRP_CREATE_STRUCTURE_LOCATIONS_ENDPOINT)
    payload = []
    queryset = Household.objects.filter(location=location)

    for item in queryset.iterator():
        serializer = HouseholdSerializer(item)
        payload.append(serializer.data)

    json_data = JSONRenderer().render(payload)

    res = send_request(url=url, payload=json_data)

    return res


def export_rhc_target_areas(rhc_id: int):
    """
    Export an entire RHC's target areas
    """
    qs = Location.objects.filter(parent__id=rhc_id, target=True)
    return export_locations(qs)
