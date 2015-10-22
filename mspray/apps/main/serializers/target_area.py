from django.conf import settings
from django.core.cache import cache
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.spraypoint import SprayPoint
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.utils import get_ta_in_location
from mspray.apps.main.utils import sprayable_queryset

SPATIAL_QUERIES = settings.MSPRAY_SPATIAL_QUERIES
WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
REASON_REFUSED = settings.MSPRAY_UNSPRAYED_REASON_REFUSED
REASONS = settings.MSPRAY_UNSPRAYED_REASON_OTHER.copy()
REASONS.pop(REASON_REFUSED)
REASON_OTHER = REASONS.keys()
HAS_UNIQUE_FIELD = getattr(settings, 'MSPRAY_UNIQUE_FIELD', None)
HAS_SPRAYABLE_QUESTION = settings.HAS_SPRAYABLE_QUESTION


def cached_queryset_count(key, queryset, query=None, params=[]):
    count = cache.get(key)

    if count is not None:
        return count

    if query is None:
        count = queryset.count()
    else:
        for item in queryset.raw(query, params):
            count = item.id
        if count is None:
            count = 0

    cache.set(key, count)

    return count


class TargetAreaMixin(object):
    def get_queryset(self, obj):

        qs = SprayDay.objects.filter(
            location__pk__in=list(get_ta_in_location(obj))
        )
        if HAS_UNIQUE_FIELD:
            qs = qs.filter(pk__in=SprayPoint.objects.values('sprayday'))

        return qs

    def get_spray_queryset(self, obj):
        pk = obj['pk'] if isinstance(obj, dict) else obj.pk
        key = '_spray_queryset_{}'.format(pk)
        if hasattr(self, key):
            return getattr(self, key)

        qs = sprayable_queryset(self.get_queryset(obj))
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

    def get_found(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_found" % pk
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
                       params=[REASON_FIELD, REASON_REFUSED])

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
                ], params=[REASON_FIELD])

            return cached_queryset_count(key, queryset)

    def get_not_visited(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            structures = obj['structures'] \
                if isinstance(obj, dict) else obj.structures
            not_sprayable = self.get_not_sprayable(obj)
            structures -= not_sprayable
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
        return obj.get('pk') if isinstance(obj, dict) else obj.pk

    def get_new_structures(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_new_structures" % pk
            queryset = self.get_spray_queryset(obj).extra(
                where=["(data->>%s) IS NULL"], params=["osmstructure"]
            )

            return cached_queryset_count(key, queryset)

        return 0

    def get_structures(self, obj):
        structures = obj.get('structures') \
            if isinstance(obj, dict) else obj.structures

        count = self.get_not_sprayable(obj)
        structures -= count
        new_structures = self.get_new_structures(obj)
        structures += new_structures

        return structures

    def get_not_sprayable(self, obj):
        count = 0
        queryset = self.get_queryset(obj)

        if HAS_SPRAYABLE_QUESTION:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            queryset = queryset.extra(
                where=['data->>%s = %s'],
                params=['sprayable_structure', 'no']
            )
            key = "%s_not_sprayable" % pk
            count = cached_queryset_count(key, queryset)

        return count


class TargetAreaQueryMixin(TargetAreaMixin):
    def get_found(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_found" % pk
            queryset = self.get_spray_queryset(obj)
            query = ("SELECT SUM((data->>'number_sprayable')::int) as id "
                     "FROM main_sprayday WHERE location_id IN %s")
            location_pks = list(get_ta_in_location(obj))
            if len(location_pks) == 0:
                return 0
            params = [tuple(location_pks)]

            return cached_queryset_count(key, queryset, query, params)

    def get_visited_sprayed(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_sprayed" % pk
            queryset = self.get_spray_queryset(obj)

            query = ("SELECT SUM((data->>'sprayed/sprayed_DDT')::int + "
                     "(data->>'sprayed/sprayed_Deltamethrin')::int) as id "
                     "FROM main_sprayday WHERE location_id IN %s")
            location_pks = list(get_ta_in_location(obj))
            if len(location_pks) == 0:
                return 0
            params = [tuple(location_pks)]

            return cached_queryset_count(key, queryset, query, params)

    def get_visited_not_sprayed(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_not_sprayed" % pk
            queryset = self.get_spray_queryset(obj)
            query = ("SELECT SUM((data->>'sprayed/sprayable_notsprayed')::int)"
                     " as id FROM main_sprayday WHERE location_id IN %s")
            location_pks = list(get_ta_in_location(obj))
            if len(location_pks) == 0:
                return 0
            params = [tuple(location_pks)]

            return cached_queryset_count(key, queryset, query, params)

    def get_visited_refused(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_refused" % pk
            queryset = self.get_spray_queryset(obj)
            query = ("SELECT SUM((data->>'sprayed/sprayable_notsprayed')::int)"
                     " as id FROM main_sprayday WHERE location_id IN %s"
                     " AND data->>%s = %s")
            location_pks = list(get_ta_in_location(obj))
            if len(location_pks) == 0:
                return 0
            params = [tuple(location_pks), REASON_FIELD, REASON_REFUSED]

            return cached_queryset_count(key, queryset, query, params)

    def get_visited_other(self, obj):
        if obj:
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            key = "%s_visited_other" % pk
            queryset = self.get_spray_queryset(obj)

            query = ("SELECT SUM((data->>'sprayed/sprayable_notsprayed')::int)"
                     " as id FROM main_sprayday WHERE location_id IN %s"
                     " AND data->>%s IN %s")
            location_pks = list(get_ta_in_location(obj))
            if len(location_pks) == 0:
                return 0
            params = [tuple(location_pks), REASON_FIELD, tuple(REASON_OTHER)]

            return cached_queryset_count(key, queryset, query, params)


class TargetAreaSerializer(TargetAreaMixin, serializers.ModelSerializer):
    targetid = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()
    spray_dates = serializers.SerializerMethodField()

    class Meta:
        fields = ('targetid', 'district_name', 'found',
                  'structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited', 'bounds', 'spray_dates', 'level')
        model = TargetArea


class TargetAreaQuerySerializer(TargetAreaQueryMixin,
                                serializers.ModelSerializer):
    targetid = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()
    spray_dates = serializers.SerializerMethodField()

    class Meta:
        fields = ('targetid', 'district_name', 'found',
                  'structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited', 'bounds', 'spray_dates', 'level')
        model = TargetArea


class GeoTargetAreaSerializer(TargetAreaMixin, GeoFeatureModelSerializer):
    targetid = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
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
                  'not_visited', 'level', 'district_name', 'found')
        model = TargetArea
        geo_field = 'geom'
