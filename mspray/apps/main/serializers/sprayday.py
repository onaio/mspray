from rest_framework_gis import serializers

from mspray.apps.main.models.spray_day import SprayDay


class SprayDaySerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = SprayDay
        geo_field = 'geom'
