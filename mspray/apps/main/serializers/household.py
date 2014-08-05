from rest_framework_gis import serializers

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.households_buffer import HouseholdsBuffer


class HouseholdSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = Household
        geo_field = 'geom'


class HouseholdsBufferSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = HouseholdsBuffer
        geo_field = 'geom'
