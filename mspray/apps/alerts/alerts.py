# -*- coding: utf-8 -*-
"""Alert functions."""


from mspray.apps.alerts.rapidpro import start_flow
from mspray.apps.alerts.serializers import SprayEffectivenessSerializer
from mspray.apps.main.models import Location, SprayDay


def daily_spray_effectiveness(flow_uuid, spray_date):
    """Sends to RapidPro a daily spray effectiveness calculations"""
    visited = (
        SprayDay.objects.filter(spray_date=spray_date)
        .exclude(location__isnull=True)
        .values_list("location", flat=True)
    )
    spray_areas = Location.objects.filter(id__in=visited)

    serializer = SprayEffectivenessSerializer(spray_areas, many=True)
    for record in serializer.data:
        start_flow(flow_uuid, payload=record)
