from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.households_buffer import HouseholdsBuffer
from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.spray_day import DATA_FILTER

ZERO_COLOR = '#CCCCCC'
_1_COLOR = '#FF4136'
_33_COLOR = '#FF851B'
_66_COLOR = '#FFDC00'
_100_COLOR = '#2ECC40'


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
                SprayDay.objects.filter(
                    geom__coveredby=obj.geom,
                    data__contains=DATA_FILTER
                ).count()

            return obj._cache_spray_points

    def get_perc_sprayed(self, obj):
        if obj:
            if obj.num_households == 0:
                return 0

            return round(
                (self.get_spray_points(obj) / obj.num_households) * 100, 2)

    def _get_color(self, obj):
        if obj:
            perc = self.get_perc_sprayed(obj)
            color = ZERO_COLOR

            if perc > 99:
                color = _100_COLOR
            elif perc > 66:
                color = _66_COLOR
            elif perc > 33:
                color = _33_COLOR
            elif perc > 0:
                color = _1_COLOR

            return color

    def to_native(self, obj):
        ret = super(HouseholdsBufferSerializer, self).to_native(obj)

        if 'style' not in ret and obj is not None:
            ret['style'] = {'fillColor': self._get_color(obj)}

        return ret
