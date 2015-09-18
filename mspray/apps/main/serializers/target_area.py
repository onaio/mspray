from django.conf import settings
from django.core.cache import cache
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.utils import get_ta_in_location
from mspray.apps.main.utils import sprayable_queryset

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
        pk = obj['pk'] if isinstance(obj, dict) else obj.pk
        key = '_spray_queryset_{}'.format(pk)

        if hasattr(self, key):
            return getattr(self, key)

        qs = SprayDay.objects.filter(
            location__pk__in=get_ta_in_location(obj)
        )
        qs = sprayable_queryset(qs)
        setattr(self, key, qs)

        return qs

    def get_spray_dates(self, obj):
        if obj:
            queryset = self.get_spray_queryset(obj)

            return queryset.values_list('spray_date', flat=True)\
                .order_by('spray_date').distinct()

    def get_visited_total(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_total" % pk
            queryset = self.get_spray_queryset(obj)

            return cached_queryset_count(key, queryset)

    def get_visited_sprayed(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_sprayed" % pk
            queryset = self.get_spray_queryset(obj)\
                .extra(where=['data->>%s = %s'],
                       params=[WAS_SPRAYED_FIELD, "yes"])

            return cached_queryset_count(key, queryset)

    def get_visited_not_sprayed(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_not_sprayed" % pk
            queryset = self.get_spray_queryset(obj)\
                .extra(where=['data->>%s = %s'],
                       params=[WAS_SPRAYED_FIELD, "no"])

            return cached_queryset_count(key, queryset)

    def get_visited_refused(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_refused" % pk
            queryset = self.get_spray_queryset(obj)\
                .extra(where=['data->>%s = %s'],
                       params=["unsprayed/reason", REASON_REFUSED])

            return cached_queryset_count(key, queryset)

    def get_visited_other(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_other" % pk
            queryset = self.get_spray_queryset(obj)\
                .extra(where=[
                    "data->>%s IN ({})".format(
                        ",".join(["'{}'".format(i) for i in REASON_OTHER])
                    )
                ], params=['unsprayed/reason'])

            return cached_queryset_count(key, queryset)

    def get_not_visited(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            structures = obj['structures'] \
                if isinstance(obj, dict) else obj.structures
            key = "%s_not_visited" % pk
            queryset = self.get_spray_queryset(obj)
            count = cached_queryset_count(key, queryset)

            return structures - count

    def get_bounds(self, obj):
        bounds = []
        if obj:
            if isinstance(obj, dict):
                bounds = [obj.get('xmin'), obj.get('ymin'),
                          obj.get('xmax'), obj.get('ymax')]
            elif obj.geom:
                bounds = list(obj.geom.boundary.extent)

        return bounds

    def get_district_name(self, obj):
        return obj.get('name') if isinstance(obj, dict) else obj.name

    def get_targetid(self, obj):
        return obj.get('code') if isinstance(obj, dict) else obj.code


class TargetAreaSerializer(TargetAreaMixin, serializers.ModelSerializer):
    targetid = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
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
                  'not_visited', 'bounds', 'spray_dates', 'level')
        model = TargetArea


class GeoTargetAreaSerializer(TargetAreaMixin, GeoFeatureModelSerializer):
    targetid = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
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
                  'not_visited', 'level', 'district_name')
        model = TargetArea
        geo_field = 'geom'
