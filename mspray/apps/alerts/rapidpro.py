from django.conf import settings

from temba_client.v2 import TembaClient


client = TembaClient(settings.RAPIDPRO_API_URL, settings.RAPIDPRO_API_TOKEN)
default_contact_uuid = settings.RAPIDPRO_DEFAULT_CONTACT_ID


class RapidProContact:

    def parse(self):
        """
        Gets and sets  contact info. from raw data
        """
        self.phones = [x[4:] for x in self.raw if x[:4] == 'tel:']
        self.emails = [y[7:] for y in self.raw if y[:7] == 'mailto:']

    def __init__(self, name, raw):
        self.name = name
        self.raw = raw
        self.parse()


def start_flow(flow_uuid, payload):
    """
    Starts a RapidPRo flow, sending the payload to the flow
    """
    return client.create_flow_start(flow_uuid, contacts=[default_contact_uuid],
                                    extra=payload)


def fetch_contacts(group_uuid):
    """
    Fetches contacts from a RapidPro group
    """
    cursor = client.get_contacts(group=group_uuid)
    return cursor.all()


def parse_contacts(fetched_contacts):
    """
    Extracts contact information from contacts returned by RapidPro
    """
    result = []
    for c in fetched_contacts:
        result.append(RapidProContact(name=c.name, raw=c.urns))
    return result


def get_contacts(group_uuid):
    """Returns RapidProContact objects fetched and parsed from a RapidPro
    contacts group"""
    fetched = fetch_contacts(group_uuid)
    return parse_contacts(fetched)
