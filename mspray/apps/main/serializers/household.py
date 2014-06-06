from rest_framework_gis import serializers

from mspray.apps.main.models.household import Household


class HouseholdSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Household
        geo_field = 'geom'


class BufferHouseholdSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Household
        geo_field = 'bgeom'
