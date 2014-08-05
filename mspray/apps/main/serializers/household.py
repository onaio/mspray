from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.households_buffer import HouseholdsBuffer
from mspray.apps.main.models.spray_day import SprayDay


class HouseholdSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Household
        geo_field = 'geom'


class HouseholdsBufferSerializer(GeoFeatureModelSerializer):
    spray_points = serializers.SerializerMethodField('get_spray_points')
    percentage_sprayed = serializers.SerializerMethodField('get_perc_sprayed')

    class Meta:
        model = HouseholdsBuffer
        geo_field = 'geom'

    def get_spray_points(self, obj):
        if obj:
            if hasattr(obj, '_cache_spray_points'):
                return obj._cache_spray_points

            obj._cache_spray_points = \
                SprayDay.objects.filter(geom__coveredby=obj.geom).count()

            return obj._cache_spray_points

    def get_perc_sprayed(self, obj):
        if obj:
            if obj.num_households == 0:
                return 0

            return round(
                (self.get_spray_points(obj) / obj.num_households) * 100, 2)
