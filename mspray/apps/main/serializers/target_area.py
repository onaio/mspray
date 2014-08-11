from django.core.cache import cache
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.target_area import TargetArea


def cached_queryset_count(key, queryset, query=None):
    count = cache.get(key)

    if count is not None:
        return count

    if query is None:
        count = queryset.count()
    else:
        for item in queryset.objects.raw(query):
            count = item.id

    cache.set(key, count)

    return count


class TargetAreaMixin(object):
    def get_visited_total(self, obj):
        if obj:
            key = "%s_visited_total" % obj.pk
            queryset = SprayDay.objects.filter(geom__coveredby=obj.geom)

            return cached_queryset_count(key, queryset)

    def get_visited_sprayed(self, obj):
        if obj:
            key = "%s_visited_sprayed" % obj.pk
            query = "SELECT Count(*) as id FROM main_sprayday "\
                " WHERE ST_CoveredBy(geom, ST_GeomFromText('SRID=4326;%s'))"\
                " AND data->>'sprayed/was_sprayed' = 'yes'" % obj.geom

            return cached_queryset_count(key, SprayDay, query)

    def get_visited_refused(self, obj):
        if obj:
            key = "%s_visited_refused" % obj.pk
            query = "SELECT Count(*) as id FROM main_sprayday "\
                " WHERE ST_CoveredBy(geom, ST_GeomFromText('SRID=4326;%s'))"\
                " AND data->>'unsprayed/reason' = '4'" % obj.geom

            return cached_queryset_count(key, SprayDay, query)

    def get_visited_other(self, obj):
        if obj:
            key = "%s_visited_other" % obj.pk
            query = "SELECT Count(*) as id FROM main_sprayday "\
                " WHERE ST_CoveredBy(geom, ST_GeomFromText('SRID=4326;%s'))"\
                " AND data->>'unsprayed/reason' = '6'" % obj.geom

            return cached_queryset_count(key, SprayDay, query)

    def get_not_visited(self, obj):
        if obj:
            key = "%s_not_visited" % obj.pk
            queryset = SprayDay.objects.filter(geom__coveredby=obj.geom)
            count = cached_queryset_count(key, queryset)

            return obj.houses - count

    def get_bounds(self, obj):
        if obj:
            return obj.geom.boundary.extent


class TargetAreaSerializer(TargetAreaMixin, serializers.ModelSerializer):
    targetid = serializers.Field(source='ranks')
    structures = serializers.Field(source='houses')
    visited_total = serializers.SerializerMethodField('get_visited_total')
    visited_sprayed = serializers.SerializerMethodField('get_visited_sprayed')
    visited_refused = serializers.SerializerMethodField('get_visited_refused')
    visited_other = serializers.SerializerMethodField('get_visited_other')
    not_visited = serializers.SerializerMethodField('get_not_visited')
    bounds = serializers.SerializerMethodField('get_bounds')

    class Meta:
        fields = ('targetid', 'structures', 'visited_total', 'visited_sprayed',
                  'visited_refused', 'visited_other', 'not_visited', 'bounds')
        model = TargetArea


class GeoTargetAreaSerializer(TargetAreaMixin, GeoFeatureModelSerializer):
    targetid = serializers.Field(source='ranks')
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
