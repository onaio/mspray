from rest_framework.renderers import BaseRenderer
from rest_framework.renderers import JSONRenderer


class CSVRenderer(BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'


class GeoJSONRenderer(JSONRenderer):
    format = 'geojson'
