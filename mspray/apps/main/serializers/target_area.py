from django.db.models import Case, Count, ExpressionWrapper, F, Func, Sum, When
from django.db.models import FloatField, IntegerField
from django.conf import settings
from django.core.cache import cache
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

from mspray.apps.main.models.location import Location
from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models.spraypoint import SprayPoint
from mspray.apps.main.models.target_area import TargetArea
from mspray.apps.main.utils import get_ta_in_location
from mspray.apps.main.utils import sprayable_queryset
from mspray.apps.main.utils import parse_spray_date

FUNCTION_TEMPLATE = '%(function)s(%(expressions)s AS FLOAT)'

SPATIAL_QUERIES = settings.MSPRAY_SPATIAL_QUERIES
TA_LEVEL = settings.MSPRAY_TA_LEVEL
WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
WAS_SPRAYED_VALUE = settings.MSPRAY_WAS_SPRAYED_VALUE
REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
REASON_REFUSED = settings.MSPRAY_UNSPRAYED_REASON_REFUSED
REASONS = settings.MSPRAY_UNSPRAYED_REASON_OTHER.copy()
REASONS.pop(REASON_REFUSED)
REASON_OTHER = REASONS.keys()
HAS_UNIQUE_FIELD = getattr(settings, 'MSPRAY_UNIQUE_FIELD', None)
HAS_SPRAYABLE_QUESTION = settings.HAS_SPRAYABLE_QUESTION


def cached_queryset_count(key, queryset, query=None, params=[]):
    count = cache.get(key) if settings.DEBUG is False else None

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


def get_spray_data(obj, context):
    request = context.get('request')
    spray_date = parse_spray_date(request) if request else None

    if type(obj) == dict:
        loc = Location.objects.get(pk=obj.get('pk'))
    else:
        loc = obj
    if loc.level in ['RHC', 'district']:
        if loc.level == 'district':
            pks = loc.spraydaydistrict_set.values('content_object_id')
        else:
            pks = loc.spraydayhealthcenterlocation_set\
                .values('content_object_id')
        qs = SprayDay.objects.filter(pk__in=pks)
        if spray_date:
            qs = qs.filter(spray_date=spray_date)

        return qs.filter(spraypoint__isnull=False).values('location')\
            .annotate(
                found=Sum(
                    Case(
                        When(
                            data__contains={WAS_SPRAYED_FIELD: 'notsprayable'},
                            was_sprayed=False,
                            then=0
                        ),
                        default=1,
                        output_field=IntegerField()
                    )
                ),
                sprayed=Sum(
                    Case(
                        When(was_sprayed=True, then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                not_sprayed=Sum(
                    Case(
                        When(
                            was_sprayed=False,
                            data__contains={WAS_SPRAYED_FIELD: 'notsprayed'},
                            then=1
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                not_sprayable=Sum(
                    Case(
                        When(
                            data__has_key='osmstructure:way:id',
                            data__contains={WAS_SPRAYED_FIELD: 'notsprayable'},
                            was_sprayed=False,
                            then=1
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                new_structures=Sum(
                    Case(
                        When(data__has_key='osmstructure:node:id', then=1),
                        When(
                            data__has_key='osmstructure:node:id',
                            data__contains={
                                WAS_SPRAYED_FIELD: 'notsprayable'
                            },
                            then=-1
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                refused=Sum(
                    Case(
                        When(
                            was_sprayed=False,
                            data__contains={REASON_FIELD: REASON_REFUSED},
                            then=1
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                other=Sum(
                    Case(
                        When(
                            was_sprayed=False,
                            data__contains={REASON_FIELD: REASON_REFUSED},
                            then=0
                        ),
                        When(
                            was_sprayed=True,
                            then=0
                        ),
                        default=1,
                        output_field=IntegerField()
                    )
                ),
                structures=F('location__structures')
            )

    qs = loc.sprayday_set
    if spray_date:
        qs = qs.filter(spray_date=spray_date)

    return qs.filter(spraypoint__isnull=False).aggregate(
        found=Sum(
            Case(
                When(
                    # data__has_key='osmstructure:way:id',
                    data__contains={WAS_SPRAYED_FIELD: 'notsprayable'},
                    was_sprayed=False,
                    then=0
                ),
                default=1,
                output_field=IntegerField()
            )
        ),
        sprayed=Sum(
            Case(
                When(was_sprayed=True, then=1),
                default=0,
                output_field=IntegerField()
            )
        ),
        not_sprayed=Sum(
            Case(
                When(
                    was_sprayed=False,
                    data__contains={WAS_SPRAYED_FIELD: 'notsprayed'},
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        not_sprayable=Sum(
            Case(
                When(
                    data__has_key='osmstructure:way:id',
                    data__contains={WAS_SPRAYED_FIELD: 'notsprayable'},
                    was_sprayed=False,
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        new_structures=Sum(
            Case(
                When(data__has_key='osmstructure:node:id', then=1),
                When(
                    data__has_key='osmstructure:node:id',
                    data__contains={
                        WAS_SPRAYED_FIELD: 'notsprayable'
                    },
                    then=-1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        refused=Sum(
            Case(
                When(
                    was_sprayed=False,
                    data__contains={REASON_FIELD: REASON_REFUSED},
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        other=Sum(
            Case(
                When(
                    was_sprayed=False,
                    data__contains={REASON_FIELD: REASON_REFUSED},
                    then=0
                ),
                When(
                    was_sprayed=True,
                    then=0
                ),
                default=1,
                output_field=IntegerField()
            )
        )
    )


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
            level = obj['level'] if isinstance(obj, dict) else obj.level
            data = get_spray_data(obj, self.context)
            if level == TA_LEVEL:
                visited_found = data.get('found') or 0
            else:
                visited_found = 0
                for i in data:
                    found = i.get('found') or 0
                    not_sprayable = i.get('not_sprayable') or 0
                    new_structures = i.get('new_structures') or 0
                    structures = i.get('structures') or 0
                    structures -= not_sprayable
                    structures += new_structures
                    if structures != 0:
                        rate = round(found * 100 / structures)
                        if rate >= 20:
                            visited_found += 1

            return visited_found

    def _get_spray_areas_with_sprayable_structures(self, obj, **kwargs):
        loc = Location.objects.get(pk=obj.get('pk')) \
            if isinstance(obj, dict) else obj

        if loc.level == 'ta':
            sp_key = key = 'sprayday'
        else:
            key = 'spraydayhealthcenterlocation' \
                if loc.level == 'RHC' else 'spraydaydistrict'
            sp_key = '%s__content_object' % key
        sp_point = '%s__spraypoint' % sp_key
        sp_structures = '%s__location__structures' % key
        sprayable_kwargs = {
            '%s__data__sprayable_structure' % sp_key: 'yes'
        }
        qs = Location.objects.filter(
            pk=loc.pk, level=loc.level, **kwargs
        ).filter(**sprayable_kwargs)\
            .annotate(
                num_new_structures=Sum(Case(When(
                    **{'%s__data__has_key' % sp_key: 'osmstructure:node:id'},
                    then=1
                ), default=0, output_field=IntegerField())),
            ).annotate(
                sprayed=Sum(Case(
                    When(**{'%s__was_sprayed' % sp_key: True}, then=1),
                    default=0,
                    output_field=IntegerField()
                )),
                not_sprayed=Sum(Case(
                    When(**{
                        '%s__was_sprayed' % sp_key: False,
                        '%s__isnull' % sp_point: False
                    }, then=1),
                    default=0,
                    output_field=IntegerField()
                )),
                found=(Count(sp_point, distinct=True)),
                found_percentage=ExpressionWrapper(
                    (
                        Count(sp_point, distinct=True) * 100 /
                        Func(
                            F(sp_structures) + F('num_new_structures'),
                            function='CAST',
                            template=FUNCTION_TEMPLATE
                        )
                    ),
                    output_field=FloatField()
                ),
                total_structures=F(sp_structures) + F('num_new_structures'),
            ).values(
                'id',
                '%s__location' % key,
                '%s__location__code' % key, 'found',
                '%s__location__structures' % key, 'found_percentage',
                'num_new_structures', 'total_structures', 'sprayed',
                'not_sprayed'
            )
        print(list(qs))

        return qs

    def get_found(self, obj):
        if obj:
            level = obj['level'] if isinstance(obj, dict) else obj.level
            data = get_spray_data(obj, self.context)
            if level == TA_LEVEL:
                found = data.get('found') or 0
            else:
                found = data.count()

            return found

    def get_visited_sprayed(self, obj):
        if obj:
            level = obj['level'] if isinstance(obj, dict) else obj.level

            data = get_spray_data(obj, self.context)
            if level == TA_LEVEL:
                visited_sprayed = data.get('sprayed') or 0
            else:
                visited_sprayed = 0
                for i in data:
                    sprayed = i.get('sprayed') or 0
                    not_sprayable = i.get('not_sprayable') or 0
                    new_structures = i.get('new_structures') or 0
                    structures = i.get('structures') or 0
                    structures -= not_sprayable
                    structures += new_structures
                    if structures != 0:
                        rate = round(sprayed * 100 / structures)
                        if rate >= 90:
                            visited_sprayed += 1

            return visited_sprayed

    def get_visited_not_sprayed(self, obj):
        if obj:
            level = obj['level'] if isinstance(obj, dict) else obj.level
            data = get_spray_data(obj, self.context)
            if level == TA_LEVEL:
                visited_not_sprayed = data.get('not_sprayed') or 0
            else:
                visited_not_sprayed = data.aggregate(
                    r=Sum('not_sprayed')
                ).get('r') or 0

            return visited_not_sprayed

    def get_visited_refused(self, obj):
        if obj:
            level = obj['level'] if isinstance(obj, dict) else obj.level
            data = get_spray_data(obj, self.context)
            if level == TA_LEVEL:
                refused = data.get('refused') or 0
            else:
                refused = data.aggregate(r=Sum('refused')).get('r') or 0

            return refused

    def get_visited_other(self, obj):
        if obj:
            level = obj['level'] if isinstance(obj, dict) else obj.level
            data = get_spray_data(obj, self.context)
            if level == TA_LEVEL:
                other = data.get('other') or 0
            else:
                other = data.aggregate(r=Sum('other')).get('r') or 0

            return other
            # pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            # key = "%s_visited_other" % pk
            # queryset = self.get_spray_queryset(obj)\
            #     .extra(where=[
            #         "data->>%s IN ({})".format(
            #             ",".join(["'{}'".format(i) for i in REASON_OTHER])
            #         )
            #     ], params=[REASON_FIELD])

            # return cached_queryset_count(key, queryset)

    def get_not_visited(self, obj):
        if obj:
            structures = obj['structures'] \
                if isinstance(obj, dict) else obj.structures
            data = get_spray_data(obj, self.context)
            level = obj['level'] if isinstance(obj, dict) else obj.level
            if level == TA_LEVEL:
                not_sprayable = data.get('not_sprayable') or 0
                new_structures = data.get('new_structures') or 0
                structures -= not_sprayable
                structures += new_structures
                count = data.get('found') or 0
            else:
                not_sprayable = \
                    data.aggregate(r=Sum('not_sprayable')).get('r') or 0
                new_structures = \
                    data.aggregate(r=Sum('new_structures')).get('r') or 0
                count = data.aggregate(r=Sum('found')).get('r') or 0
                structures -= not_sprayable
                structures += new_structures

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
            level = obj['level'] if isinstance(obj, dict) else obj.level
            data = get_spray_data(obj, self.context)
            if level == TA_LEVEL:
                new_structures = data.get('new_structures') or 0
            else:
                new_structures = \
                    data.aggregate(r=Sum('new_structures')).get('r') or 0

            return new_structures

        return 0

    def get_structures(self, obj):
        structures = obj.get('structures') \
            if isinstance(obj, dict) else obj.structures
        data = get_spray_data(obj, self.context)
        level = obj['level'] if isinstance(obj, dict) else obj.level
        if level == TA_LEVEL:
            not_sprayable = data.get('not_sprayable') or 0
            new_structures = data.get('new_structures') or 0
            structures -= not_sprayable
            structures += new_structures
        else:
            not_sprayable = \
                data.aggregate(r=Sum('not_sprayable')).get('r') or 0
            new_structures = \
                data.aggregate(r=Sum('new_structures')) .get('r') or 0
            structures -= not_sprayable
            structures += new_structures

        return structures

    def get_not_sprayable(self, obj):
        data = get_spray_data(obj, self.context)
        level = obj['level'] if isinstance(obj, dict) else obj.level
        if level == TA_LEVEL:
            not_sprayable = data.get('not_sprayable') or 0
        else:
            not_sprayable = \
                data.aggregate(r=Sum('not_sprayable')).get('r') or 0

        return not_sprayable


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
    total_structures = serializers.IntegerField()
    num_new_structures = serializers.IntegerField()
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
                  'not_visited', 'bounds', 'spray_dates', 'level',
                  'num_of_spray_areas', 'total_structures',
                  'num_new_structures')
        model = Location


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
    total_structures = serializers.IntegerField()
    num_new_structures = serializers.IntegerField()
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
                  'not_visited', 'level', 'district_name', 'found',
                  'total_structures', 'num_new_structures',
                  'num_of_spray_areas')
        model = Location
        geo_field = 'geom'


class GeoHealthFacilitySerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Location
        geo_field = 'geom'
