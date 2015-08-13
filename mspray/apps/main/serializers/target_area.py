from django.core.cache import cache
from django.db.models import Q
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

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
            queryset = SprayDay.objects.filter(
                geom__coveredby=obj.geom
            ).filter(data__contains='"sprayable_structure":"yes"')

            return cached_queryset_count(key, queryset)

    def get_visited_sprayed(self, obj):
        if obj:
            key = "%s_visited_sprayed" % obj.pk
            queryset = SprayDay.objects.filter(
                geom__coveredby=obj.geom
            ).filter(data__contains='"sprayed/was_sprayed":"yes"')

            return cached_queryset_count(key, queryset)

    def get_visited_not_sprayed(self, obj):
        if obj:
            key = "%s_visited_not_sprayed" % obj.pk
            queryset = SprayDay.objects.filter(
                geom__coveredby=obj.geom
            ).filter(data__contains='"sprayed/was_sprayed":"no"')

            return cached_queryset_count(key, queryset)

    def get_visited_refused(self, obj):
        if obj:
            key = "%s_visited_refused" % obj.pk
            queryset = SprayDay.objects.filter(
                geom__coveredby=obj.geom
            ).filter(data__contains='"unsprayed/reason":"Refused"')

            return cached_queryset_count(key, queryset)

    def get_visited_other(self, obj):
        if obj:
            key = "%s_visited_other" % obj.pk
            queryset = SprayDay.objects.filter(
                geom__coveredby=obj.geom
            ).filter(
                Q(data__contains='"unsprayed/reason":"Other"') |
                Q(data__contains='"unsprayed/reason":"Sick"') |
                Q(data__contains='"unsprayed/reason":"Funeral"') |
                Q(data__contains='"unsprayed/reason":"Locked"') |
                Q(data__contains='"unsprayed/reason":"No one home/Missed"'))

            return cached_queryset_count(key, queryset)

    def get_not_visited(self, obj):
        if obj:
            key = "%s_not_visited" % obj.pk
            queryset = SprayDay.objects.filter(
                geom__coveredby=obj.geom
            ).filter(data__contains='"sprayable_structure":"yes"')
            count = cached_queryset_count(key, queryset)

            return obj.houses - count

    def get_bounds(self, obj):
        if obj:
            return obj.geom.boundary.extent


class TargetAreaByDataMixin(object):

    def get_visited_total(self, obj):
        if obj:
            key = "%s_visited_total" % obj.pk
            queryset = SprayDay.objects.filter(
                data__contains='"fokontany":"{}"'.format(obj.district_name)
            ).filter(data__contains='"sprayable_structure":"yes"')

            return cached_queryset_count(key, queryset)

    def get_visited_sprayed(self, obj):
        if obj:
            key = "%s_visited_sprayed" % obj.pk
            queryset = SprayDay.objects.filter(
                data__contains='"fokontany":"{}"'.format(obj.district_name)
            ).filter(data__contains='"sprayed/was_sprayed":"yes"')

            return cached_queryset_count(key, queryset)

    def get_visited_not_sprayed(self, obj):
        if obj:
            key = "%s_visited_not_sprayed" % obj.pk
            queryset = SprayDay.objects.filter(
                data__contains='"fokontany":"{}"'.format(obj.district_name)
            ).filter(data__contains='"sprayed/was_sprayed":"no"')

            return cached_queryset_count(key, queryset)

    def get_visited_refused(self, obj):
        if obj:
            key = "%s_visited_refused" % obj.pk
            queryset = SprayDay.objects.filter(
                data__contains='"fokontany":"{}"'.format(obj.district_name)
            ).filter(data__contains='"unsprayed/reason":"Refused"')

            return cached_queryset_count(key, queryset)

    def get_visited_other(self, obj):
        if obj:
            key = "%s_visited_other" % obj.pk
            queryset = SprayDay.objects.filter(
                data__contains='"fokontany":"{}"'.format(obj.district_name)
            ).filter(
                Q(data__contains='"unsprayed/reason":"Other"') |
                Q(data__contains='"unsprayed/reason":"Sick"') |
                Q(data__contains='"unsprayed/reason":"Funeral"') |
                Q(data__contains='"unsprayed/reason":"Locked"') |
                Q(data__contains='"unsprayed/reason":"No one home/Missed"'))

            return cached_queryset_count(key, queryset)

    def get_not_visited(self, obj):
        if obj:
            key = "%s_not_visited" % obj.pk
            queryset = SprayDay.objects.filter(
                data__contains='"fokontany":"{}"'.format(obj.district_name)
            ).filter(data__contains='"sprayable_structure":"yes"')
            count = cached_queryset_count(key, queryset)

            return obj.houses - count

    def get_bounds(self, obj):
        if obj and obj.geom:
            return obj.geom.boundary.extent


class TargetAreaByDataSerializer(TargetAreaByDataMixin,
                                 serializers.ModelSerializer):
    targetid = serializers.ReadOnlyField()
    structures = serializers.ReadOnlyField(source='houses')
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()

    class Meta:
        fields = ('pk', 'targetid', 'district_name',
                  'structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited', 'bounds')
        model = TargetArea


class TargetAreaSerializer(TargetAreaMixin, serializers.ModelSerializer):
    targetid = serializers.ReadOnlyField()
    structures = serializers.ReadOnlyField(source='houses')
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()

    class Meta:
        fields = ('targetid', 'district_name',
                  'structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited', 'bounds')
        model = TargetArea


class GeoTargetAreaSerializer(TargetAreaMixin, GeoFeatureModelSerializer):
    targetid = serializers.ReadOnlyField()
    structures = serializers.ReadOnlyField(source='houses')
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    geom = GeometryField()

    class Meta:
        fields = ('targetid', 'structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited')
        model = TargetArea
        geo_field = 'geom'
