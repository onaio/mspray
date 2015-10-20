from __future__ import absolute_import

from django.conf import settings

from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay
from mspray.apps.main.ona import fetch_osm_xml
from mspray.apps.main.osm import parse_osm_ways
from mspray.apps.main.osm import parse_osm_nodes
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
            osmstructure = sp.data.get('osmstructure')
            geoms = []
            is_node = osmstructure and osmstructure.startswith('OSMNode')
            if is_node:
                geoms = parse_osm_nodes(osm_xml)
            else:
                geoms = parse_osm_ways(osm_xml)
            if len(geoms):
                geom = geoms[0]
                locations = Location.objects.filter(
                    geom__covers=geom.centroid if not is_node else geom,
                    level=settings.MSPRAY_TA_LEVEL
                )
                if locations:
                    location = locations.first()
                    sp.geom = geom.centroid if not is_node else geom
                    sp.bgeom = geom \
                        if not is_node else sp.geom.buffer(0.00004, 1)
                    sp.location = location
                    sp.save()
                    if unique_field:
                        add_unique_data(sp, unique_field, location)

                    return sp.pk
                else:
                    district = sp.data.get('district')
                    target_area = sp.data.get('target_area')
                    try:
                        location = Location.objects.get(name=target_area,
                                                        parent__code=district)
                    except Location.DoesNotExist:
                        pass
                    else:
                        sp.geom = geom.centroid if not is_node else geom
                        sp.bgeom = geom \
                            if not is_node else sp.geom.buffer(0.00004, 1)
                        sp.location = location
                        sp.save()
                        if unique_field:
                            add_unique_data(sp, unique_field, location)
