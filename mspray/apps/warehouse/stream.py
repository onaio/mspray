from rest_framework.renderers import JSONRenderer

from django.conf import settings

from mspray.apps.warehouse.serializers import SprayDayDruidSerializer
from mspray.apps.warehouse.utils import send_request


def send_to_tranquility(sprayday_obj):
    data = SprayDayDruidSerializer(sprayday_obj).data
    json_data = JSONRenderer().render(data)
    return send_request(json_data, settings.DRUID_SPRAYDAY_TRANQUILITY_URI)
