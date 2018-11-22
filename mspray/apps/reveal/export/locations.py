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

    serializer = LocationSerializer(queryset, many=True)
    json_data = JSONRenderer().render(serializer.data)
    res = send_request(url=url, payload=json_data)

    return res


def export_households(location):
    """
    Export households from one target area in bulk
    """
    url = urljoin(settings.REVEAL_OPENSRP_BASE_URL,
                  settings.REVEAL_OPENSRP_CREATE_STRUCTURE_LOCATIONS_ENDPOINT)
    queryset = Household.objects.filter(location=location)

    serializer = HouseholdSerializer(queryset, many=True)
    json_data = JSONRenderer().render(serializer.data)
    res = send_request(url=url, payload=json_data)

    return res


def export_rhc_target_areas(rhc_id: int):
    """
    Export an entire RHC's target areas
    """
    qs = Location.objects.filter(parent__id=rhc_id)
    return export_locations(qs)


def export_district(district_id: int):
    """
    Export an entire district

    THIS WILL BE REFACTORED INTO A COMMAND
    """
    district_qs = Location.objects.filter(id=district_id)
    if district_qs:
        print(f'Exporting district {district_qs.first().name}')
        district_res = export_locations(district_qs)
        if district_res:
            print('Success')
            rhc_qs = Location.objects.filter(parent__id=district_id)
            print(f'Exporting RHCs in {district_qs.first().name}')
            rhc_res = export_locations(rhc_qs)
            if rhc_res:
                print('Success')
                for rhc in rhc_qs:
                    print(f'Exporting target areas in {rhc.name}')
                    ta_res = export_rhc_target_areas(rhc_id=rhc.id)
                    if ta_res:
                        print('Success')
                        ta_qs = Location.objects.filter(parent=rhc)
                        for ta in ta_qs:
                            print(f'Exporting structures in {ta.name}')
                            export_households(location=ta)
