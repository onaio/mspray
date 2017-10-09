from django.conf import settings

from temba_client.v2 import TembaClient


client = TembaClient(settings.RAPIDPRO_API_URL, settings.RAPIDPRO_API_TOKEN)
default_contact_uuid = settings.RAPIDPRO_DEFAULT_CONTACT_ID


def start_flow(flow_uuid, payload):
    """
    Starts a RapidPRo flow, sending the payload to the flow
    """
    return client.create_flow_start(flow_uuid, contacts=[default_contact_uuid],
                                    extra=payload)
