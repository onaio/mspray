from rest_framework_gis import serializers

from mspray.apps.main.models.target_area import TargetArea


class TargetAreaSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = TargetArea
        geo_field = 'geom'
