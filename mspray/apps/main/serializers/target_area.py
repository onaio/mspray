from django.db.models import Case, Count, F, Sum, When, Q
from django.db.models import IntegerField
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
WAS_NOT_SPRAYED_VALUE = settings.MSPRAY_WAS_NOT_SPRAYED_VALUE
REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
REASON_REFUSED = settings.MSPRAY_UNSPRAYED_REASON_REFUSED
REASONS = settings.MSPRAY_UNSPRAYED_REASON_OTHER.copy()
REASONS.pop(REASON_REFUSED)
REASON_OTHER = REASONS.keys()
HAS_UNIQUE_FIELD = getattr(settings, 'MSPRAY_UNIQUE_FIELD', None)
HAS_SPRAYABLE_QUESTION = settings.HAS_SPRAYABLE_QUESTION
SPRAYABLE_FIELD = settings.SPRAYABLE_FIELD
NOT_SPRAYABLE_VALUE = settings.NOT_SPRAYABLE_VALUE


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
            kwargs = {'district': loc}
        else:
            kwargs = {'rhc': loc}
        qs = SprayDay.objects.filter(**kwargs)
        if spray_date:
            qs = qs.filter(spray_date=spray_date)

        return qs.values('location')\
            .annotate(
                found=Sum(
                    Case(
                        When(
                            data__has_key=WAS_SPRAYED_FIELD,
                            spraypoint__isnull=False,
                            then=1
                        ),
                        When(
                            spraypoint__isnull=True,
                            data__has_key='newstructure/gps',
                            then=1
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                sprayed=Sum(
                    Case(
                        When(
                            was_sprayed=True,
                            spraypoint__isnull=False,
                            then=1
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                not_sprayed=Sum(
                    Case(
                        When(
                            was_sprayed=False,
                            spraypoint__isnull=False,
                            data__contains={WAS_SPRAYED_FIELD:
                                            WAS_NOT_SPRAYED_VALUE},
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
                            data__contains={SPRAYABLE_FIELD:
                                            NOT_SPRAYABLE_VALUE},
                            spraypoint__isnull=False,
                            then=1
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                new_structures=Sum(
                    Case(
                        When(
                            ~Q(data__contains={SPRAYABLE_FIELD:
                                               NOT_SPRAYABLE_VALUE}),
                            spraypoint__isnull=False,
                            data__has_key='newstructure/gps',
                            then=1
                        ),
                        When(
                            ~Q(data__contains={SPRAYABLE_FIELD:
                                               NOT_SPRAYABLE_VALUE}),
                            spraypoint__isnull=False,
                            data__has_key='osmstructure:node:id',
                            then=1
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                ),
                refused=Sum(
                    Case(
                        When(
                            was_sprayed=False,
                            spraypoint__isnull=False,
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
                            spraypoint__isnull=False,
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

    return qs.aggregate(
        found=Sum(
            Case(
                When(
                    spraypoint__isnull=False,
                    data__has_key=WAS_SPRAYED_FIELD,
                    then=1
                ),
                When(
                    spraypoint__isnull=True,
                    # data__has_key='newstructure/gps',
                    was_sprayed=True,
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        sprayed=Sum(
            Case(
                When(
                    # spraypoint__isnull=False,
                    was_sprayed=True,
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        not_sprayed=Sum(
            Case(
                When(
                    spraypoint__isnull=False,
                    was_sprayed=False,
                    data__contains={WAS_SPRAYED_FIELD: WAS_NOT_SPRAYED_VALUE},
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
                    data__contains={SPRAYABLE_FIELD:
                                    NOT_SPRAYABLE_VALUE},
                    spraypoint__isnull=False,
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        new_structures=Sum(
            Case(
                When(
                    ~Q(data__contains={SPRAYABLE_FIELD: NOT_SPRAYABLE_VALUE}),
                    # spraypoint__isnull=False,
                    data__has_key='newstructure/gps',
                    then=1
                ),
                When(
                    ~Q(data__contains={SPRAYABLE_FIELD: NOT_SPRAYABLE_VALUE}),
                    spraypoint__isnull=False,
                    data__has_key='osmstructure:node:id',
                    then=1
                ),
                When(
                    ~Q(data__contains={SPRAYABLE_FIELD: NOT_SPRAYABLE_VALUE}),
                    spraypoint__isnull=True,
                    was_sprayed=True,
                    data__has_key='osmstructure:node:id',
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        refused=Sum(
            Case(
                When(
                    spraypoint__isnull=False,
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
                    spraypoint__isnull=False,
                    was_sprayed=False,
                    data__contains={REASON_FIELD: REASON_REFUSED},
                    then=0
                ),
                When(
                    spraypoint__isnull=False,
                    was_sprayed=True,
                    then=0
                ),
                default=1,
                output_field=IntegerField()
            )
        )
    )


def get_duplicates(obj, was_sprayed):
    def duplicates(spray_status):
        return loc.sprayday_set.filter(
            osmid__isnull=False, was_sprayed=spray_status
        ).values('osmid').annotate(
            dupes=Count('osmid')
        ).filter(dupes__gt=1)

    loc = Location.objects.get(pk=obj.get('pk') or obj.get('location')) \
        if type(obj) == dict else obj
    dupes = duplicates(was_sprayed)

    if not was_sprayed:
        sprayed = duplicates(True).values_list('osmid', flat=True)
        dupes = dupes.exclude(spraypoint__isnull=False)\
            .exclude(osmid__in=sprayed)

    return dupes


def count_duplicates(obj, was_sprayed):
    dupes = get_duplicates(obj, was_sprayed)

    return sum([i.get('dupes') - 1 for i in dupes])


def count_if(data, percentage, debug=False):
    """Count as 1 if it matches the percentage or greater"""
    visited_sprayed = 0
    for i in data:
        pk = i.get('location')
        sprayed = i.get('sprayed') or 0
        not_sprayable = i.get('not_sprayable') or 0
        new_structures = i.get('new_structures') or 0
        structures = i.get('structures') or 0
        if debug:
            print(pk, "Sprayed:", sprayed, "S:", structures,
                  'NW:', new_structures, 'NS:', not_sprayable,
                  'D:', count_duplicates(i, True) if pk else '')
        structures -= not_sprayable
        structures += new_structures
        if pk is not None:
            structures += count_duplicates(i, True)
        if structures != 0:
            rate = round(sprayed * 100 / structures)
            if rate >= percentage:
                visited_sprayed += 1

    return visited_sprayed


def get_spray_area_count(location, context=dict()):
    data = get_spray_data(location, context)
    sprayed = data.get('sprayed')
    structures = (
        location.structures +
        (data.get('new_structures') or 0) +
        count_duplicates(location, True) -
        (data.get('not_sprayable') or 0)
    )

    return sprayed, structures


def count_key_if_percent(obj, key, percentage, context=dict()):
    def count_for(location):
        counter = 0
        for i in location.location_set.all():
            sprayed, structures = get_spray_area_count(i, context)
            ratio = round((sprayed * 100) / structures) if sprayed else 0
            counter += 1 if ratio >= percentage else 0

        return counter

    loc = Location.objects.get(pk=obj.get('pk')) if type(obj) == dict else obj

    if loc.level == 'RHC':
        return count_for(loc)

    return sum([count_key_if_percent(i, key, percentage, context)
                for i in loc.location_set.all()])


class DistrictMixin(object):
    def get_targetid(self, obj):
        return obj.get('pk') if isinstance(obj, dict) else obj.pk

    def get_district_name(self, obj):
        return obj.get('name') if isinstance(obj, dict) else obj.name

    def get_found(self, obj):
        return obj.get('found') or 0 if isinstance(obj, dict) else obj.found

    def get_visited_total(self, obj):
        # visited_found = count_key_if_percent(
        #     obj, 'sprayed', 20, self.context
        # )
        # return 0  # visited_found
        return obj.get('visited') if isinstance(obj, dict) else obj.visited

    def get_not_visited(self, obj):
        return obj.get('not_visited') or 0\
            if isinstance(obj, dict) else obj.not_visited

    def get_visited_other(self, obj):
        return obj.get('visited_other') or 0\
            if isinstance(obj, dict) else obj.visited_other

    def get_visited_refused(self, obj):
        return obj.get('visited_refused') or 0\
            if isinstance(obj, dict) else obj.visited_refused

    def get_visited_not_sprayed(self, obj):
        return obj.get('visited_not_sprayed') or 0 \
            if isinstance(obj, dict) else obj.visited_not_sprayed

    def get_visited_sprayed(self, obj):
        return obj.get('sprayed') if isinstance(obj, dict) else obj.sprayed

    def get_structures(self, obj):
        return obj.get('structures') \
            if isinstance(obj, dict) else obj.structures

    def get_bounds(self, obj):
        bounds = []
        if obj:
            if isinstance(obj, dict):
                bounds = [obj.get('xmin'), obj.get('ymin'),
                          obj.get('xmax'), obj.get('ymax')]
            elif obj.geom:
                bounds = list(obj.geom.boundary.extent)

        return bounds

    def get_spray_dates(self, obj):
        if obj:
            # level = obj['level'] if isinstance(obj, dict) else obj.level
            pk = obj['pk'] if isinstance(obj, dict) else obj.pk
            location = Location.objects.get(pk=pk)
            queryset = location.visited_district.all()

            return queryset.values_list('spray_date', flat=True)\
                .order_by('spray_date').distinct()


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
            if level == TA_LEVEL:
                data = get_spray_data(obj, self.context)
                visited_found = (data.get('found') or 0)
            else:
                visited_found = count_key_if_percent(
                    obj, 'sprayed', 20, self.context
                )

            return visited_found

    def get_found(self, obj):
        if obj:
            level = obj['level'] if isinstance(obj, dict) else obj.level
            data = get_spray_data(obj, self.context)
            if level == TA_LEVEL:
                found = (data.get('found') or 0)
            else:
                found = data.count()

            return found

    def get_visited_sprayed(self, obj):
        if obj:
            level = obj['level'] if isinstance(obj, dict) else obj.level

            if level == TA_LEVEL:
                data = get_spray_data(obj, self.context)
                visited_sprayed = data.get('sprayed') or 0
            else:
                visited_sprayed = count_key_if_percent(
                    obj, 'sprayed', 85, self.context
                )

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
                structures += new_structures + count_duplicates(obj, True)
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
            structures += new_structures + count_duplicates(obj,
                                                            was_sprayed=True)
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
    district = serializers.SerializerMethodField()
    district_pk = serializers.SerializerMethodField()
    rhc = serializers.SerializerMethodField()
    rhc_pk = serializers.SerializerMethodField()
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
                  'num_of_spray_areas', 'total_structures', 'district', 'rhc',
                  'district_pk', 'rhc_pk',
                  'num_new_structures')
        model = Location

    def get_district(self, obj):
        if obj:
            try:
                return obj.get('parent__parent__name') \
                    if isinstance(obj, dict) else obj.parent.parent.name
            except:
                pass

    def get_district_pk(self, obj):
        if obj:
            try:
                return obj.get('parent__parent__pk') \
                    if isinstance(obj, dict) else obj.parent.parent.pk
            except:
                pass

    def get_rhc(self, obj):
        if obj:
            try:
                return obj.get('parent__name') \
                    if isinstance(obj, dict) else obj.parent.name
            except:
                pass

    def get_rhc_pk(self, obj):
        if obj:
            try:
                return obj.get('parent__pk') \
                    if isinstance(obj, dict) else obj.parent.pk
            except:
                pass


class DistrictSerializer(DistrictMixin, serializers.ModelSerializer):
    targetid = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    district_pk = serializers.SerializerMethodField()
    rhc = serializers.SerializerMethodField()
    rhc_pk = serializers.SerializerMethodField()
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
                  'num_of_spray_areas', 'total_structures', 'district', 'rhc',
                  'district_pk', 'rhc_pk',
                  'num_new_structures')
        model = Location

    def get_district(self, obj):
        if obj:
            try:
                return obj.get('parent__parent__name') \
                    if isinstance(obj, dict) else obj.parent.parent.name
            except:
                pass

    def get_district_pk(self, obj):
        if obj:
            try:
                return obj.get('parent__parent__pk') \
                    if isinstance(obj, dict) else obj.parent.parent.pk
            except:
                pass

    def get_rhc(self, obj):
        if obj:
            try:
                return obj.get('parent__name') \
                    if isinstance(obj, dict) else obj.parent.name
            except:
                pass

    def get_rhc_pk(self, obj):
        if obj:
            try:
                return obj.get('parent__pk') \
                    if isinstance(obj, dict) else obj.parent.pk
            except:
                pass


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
