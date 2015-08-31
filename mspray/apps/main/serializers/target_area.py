from django.conf import settings
from django.core.cache import cache
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.target_area import TargetArea

SPATIAL_QUERIES = settings.MSPRAY_SPATIAL_QUERIES
WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
REASON_REFUSED = settings.MSPRAY_UNSPRAYED_REASON_REFUSED
REASON_OTHER = settings.MSPRAY_UNSPRAYED_REASON_OTHER.keys()


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
    def get_spray_queryset(self, obj):
        if SPATIAL_QUERIES:
            return SprayDay.objects.filter(geom__covered_by=obj.geom)

        if obj.parent is None:
            return SprayDay.objects.filter(location__parent=obj)

        return SprayDay.objects.filter(location=obj)

    def get_spray_dates(self, obj):
        if obj:
            queryset = self.get_spray_queryset(obj)
            # .filter(data__contains='"sprayable_structure":"yes"')

            return queryset.values_list('spray_date', flat=True).distinct()

    def get_visited_total(self, obj):
        if obj:
            key = "%s_visited_total" % obj.pk
            queryset = self.get_spray_queryset(obj)
            #    .filter(data__contains='"sprayable_structure":"yes"')

            return cached_queryset_count(key, queryset)

    def get_visited_sprayed(self, obj):
        if obj:
            key = "%s_visited_sprayed" % obj.pk
            queryset = self.get_spray_queryset(obj)\
                .filter(data__contains='"{}":"yes"'.format(WAS_SPRAYED_FIELD))

            return cached_queryset_count(key, queryset)

    def get_visited_not_sprayed(self, obj):
        if obj:
            key = "%s_visited_not_sprayed" % obj.pk
            queryset = self.get_spray_queryset(obj)\
                .filter(data__contains='"{}":"no"'.format(WAS_SPRAYED_FIELD))

            return cached_queryset_count(key, queryset)

    def get_visited_refused(self, obj):
        if obj:
            key = "%s_visited_refused" % obj.pk
            queryset = self.get_spray_queryset(obj)\
                .filter(data__contains='"unsprayed/reason":"{}"'.format(
                    REASON_REFUSED)
                )

            return cached_queryset_count(key, queryset)

    def get_visited_other(self, obj):
        if obj:
            key = "%s_visited_other" % obj.pk
            queryset = self.get_spray_queryset(obj)\
                .extra(where=[
                    "data->>%s IN ({})".format(
                        ",".join(["'{}'".format(i) for i in REASON_OTHER])
                    )
                ], params=['unsprayed/reason'])

            return cached_queryset_count(key, queryset)

    def get_not_visited(self, obj):
        if obj:
            key = "%s_not_visited" % obj.pk
            queryset = self.get_spray_queryset(obj)
            #    .filter(data__contains='"sprayable_structure":"yes"')
            count = cached_queryset_count(key, queryset)

            return obj.structures - count

    def get_bounds(self, obj):
        if obj and obj.geom:
            return list(obj.geom.boundary.extent)

        return []


class TargetAreaSerializer(TargetAreaMixin, serializers.ModelSerializer):
    targetid = serializers.ReadOnlyField()
    structures = serializers.ReadOnlyField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()
    spray_dates = serializers.SerializerMethodField()

    class Meta:
        fields = ('targetid', 'district_name',
                  'structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited', 'bounds', 'spray_dates')
        model = TargetArea


class GeoTargetAreaSerializer(TargetAreaMixin, GeoFeatureModelSerializer):
    targetid = serializers.ReadOnlyField()
    structures = serializers.ReadOnlyField()
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
