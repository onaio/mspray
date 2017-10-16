from rest_framework.renderers import JSONRenderer

from django.conf import settings

from mspray.apps.warehouse.serializers import SprayDayDruidSerializer
from mspray.apps.warehouse.utils import send_request


def get_mspray_stream_url():
    return "{}:{}{}".format(settings.DRUID_SPRAYDAY_TRANQUILITY_URI,
                            settings.DRUID_SPRAYDAY_TRANQUILITY_PORT,
                            settings.DRUID_SPRAYDAY_TRANQUILITY_PATH)


def send_to_tranquility(sprayday_obj):
    data = SprayDayDruidSerializer(sprayday_obj).data
    json_data = JSONRenderer().render(data)
    return send_request(json_data, get_mspray_stream_url())
