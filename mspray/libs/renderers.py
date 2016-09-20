from rest_framework.renderers import (JSONRenderer, BaseRenderer)
from mspray.apps.main.osm import generate_osm_xml


class GeoJSONRenderer(JSONRenderer):
    format = 'geojson'


class OSMRenderer(BaseRenderer):
    media_type = 'text/xml'
    format = 'osm'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, dict) and 'detail' in data:
            return u'<error>' + data['detail'] + '</error>'

        return generate_osm_xml(data)
