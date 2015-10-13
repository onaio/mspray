from __future__ import absolute_import

from django.conf import settings

from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay
from mspray.apps.main.ona import fetch_osm_xml
from mspray.apps.main.osm import parse_osm_ways
from mspray.celery import app

HAS_UNIQUE_FIELD = getattr(settings, 'MSPRAY_UNIQUE_FIELD', None)


@app.task
def link_spraypoint_with_osm(pk):
    try:
        sp = SprayDay.objects.get(pk=pk)
    except SprayDay.DoesNotExist:
        pass
    else:
        from mspray.apps.main.utils import add_unique_data
        unique_field = HAS_UNIQUE_FIELD
        osm_xml = fetch_osm_xml(sp.data)
        if osm_xml is not None:
            ways = parse_osm_ways(osm_xml)
            if len(ways):
                way = ways[0]
                locations = Location.objects.filter(
                    geom__covers=way.centroid,
                    level=settings.MSPRAY_TA_LEVEL
                )
                if locations.count():
                    location = locations.first()
                    sp.geom = way.centroid
                    sp.bgeom = way
                    sp.location = location
                    sp.save()
                    if unique_field:
                        add_unique_data(sp, unique_field, location)

                    return sp.pk
