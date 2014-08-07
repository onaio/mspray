from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.main.models.household import Household
from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.target_area import TargetArea


class TargetAreaMixin(object):
    def get_visited_total(self, obj):
        if obj:
            return SprayDay.objects.filter(geom__coveredby=obj.geom).count()

    def get_visited_sprayed(self, obj):
        if obj:
            return SprayDay.objects.filter(geom__coveredby=obj.geom).count()

    def get_visited_refused(self, obj):
        if obj:
            return obj.houses - SprayDay.objects.filter(
                geom__coveredby=obj.geom).count()

    def get_visited_other(self, obj):
        if obj:
            hh = Household.objects.filter(geom__coveredby=obj.geom).count()
            sp = SprayDay.objects.filter(geom__coveredby=obj.geom).count()

            return hh - sp

    def get_not_visited(self, obj):
        if obj:
            return obj.houses - SprayDay.objects.filter(
                geom__coveredby=obj.geom).count()


class TargetAreaSerializer(TargetAreaMixin, serializers.ModelSerializer):
    structures = serializers.Field(source='houses')
    visited_total = serializers.SerializerMethodField('get_visited_total')
    visited_sprayed = serializers.SerializerMethodField('get_visited_sprayed')
    visited_refused = serializers.SerializerMethodField('get_visited_refused')
    visited_other = serializers.SerializerMethodField('get_visited_other')
    not_visited = serializers.SerializerMethodField('get_not_visited')

    class Meta:
        fields = ('targetid', 'structures', 'visited_total', 'visited_sprayed',
                  'visited_refused', 'visited_other', 'not_visited')
        model = TargetArea


class GeoTargetAreaSerializer(TargetAreaMixin, GeoFeatureModelSerializer):
    structures = serializers.Field(source='houses')
    visited_total = serializers.SerializerMethodField('get_visited_total')
    visited_sprayed = serializers.SerializerMethodField('get_visited_sprayed')
    visited_refused = serializers.SerializerMethodField('get_visited_refused')
    visited_other = serializers.SerializerMethodField('get_visited_other')
    not_visited = serializers.SerializerMethodField('get_not_visited')

    class Meta:
        fields = ('targetid', 'structures', 'visited_total', 'visited_sprayed',
                  'visited_refused', 'visited_other', 'not_visited')
        model = TargetArea
        geo_field = 'geom'
