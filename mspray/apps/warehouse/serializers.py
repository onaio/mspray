import operator
from dateutil import parser
import pytz

from django.conf import settings
from django.urls import reverse

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

from mspray.apps.main.models import SprayDay, Location, Household
from mspray.apps.main.serializers.sprayday import SprayBase
from mspray.apps.warehouse.druid import get_druid_data, druid_simple_groupby
from mspray.apps.warehouse.utils import flatten

REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD


class LocationMixin(object):

    def get_location_id(self, obj):
        if obj and obj.location:
            return obj.location.id

    def get_location_name(self, obj):
        if obj and obj.location:
            return obj.location.name

    def get_target_area_id(self, obj):
        if obj and obj.location:
            return obj.location.id

    def get_target_area_name(self, obj):
        if obj and obj.location:
            return obj.location.name

    def get_target_area_structures(self, obj):
        if obj and obj.location:
            return obj.location.structures

    def get_rhc_id(self, obj):
        if obj and obj.location:
            this_rhc = obj.location.get_family().filter(level='RHC').first()
            if this_rhc:
                return this_rhc.id

    def get_rhc_name(self, obj):
        if obj and obj.location:
            this_rhc = obj.location.get_family().filter(level='RHC').first()
            if this_rhc:
                return this_rhc.name

    def get_rhc_structures(self, obj):
        if obj and obj.location:
            this_rhc = obj.location.get_family().filter(level='RHC').first()
            if this_rhc:
                return this_rhc.structures

    def get_district_id(self, obj):
        if obj and obj.location:
            this_district = obj.location.get_family().filter(
                level='district').first()
            if this_district:
                return this_district.id

    def get_district_name(self, obj):
        if obj and obj.location:
            this_district = obj.location.get_family().filter(
                level='district').first()
            if this_district:
                return this_district.name

    def get_district_structures(self, obj):
        if obj and obj.location:
            this_district = obj.location.get_family().filter(
                level='district').first()
            if this_district:
                return this_district.structures


class HouseHoldDruidSerializer(LocationMixin, serializers.ModelSerializer):
    """
    Used to store Household objects in Druid
    """
    timestamp = serializers.SerializerMethodField()
    target_area_id = serializers.SerializerMethodField()
    target_area_name = serializers.SerializerMethodField()
    rhc_id = serializers.SerializerMethodField()
    rhc_name = serializers.SerializerMethodField()
    district_id = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    building = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = ['id', 'target_area_id', 'target_area_name', 'rhc_id',
                  'rhc_name', 'district_id', 'district_name', 'building',
                  'source', 'timestamp']

    def get_timestamp(self, obj):
        """
        Household objects do not have a timestamp, but this is needed for
        Druid.
        We therefore create one, and we make sure it is always the same for
        each object, so that we can update Druid for the same record
        """
        timestring = getattr(settings, "HOUSEHOLD_DATETIME",
                             "2017-09-30 16:20:00")
        datetime_obj = pytz.timezone("UTC").localize(
            parser.parse(timestring), is_dst=None)
        return datetime_obj

    def get_building(self, obj):
        if obj and obj.data:
            return flatten(obj.data).get('building')

    def get_source(self, obj):
        if obj and obj.data:
            return flatten(obj.data).get('source')


class SprayDayDruidSerializer(SprayBase, LocationMixin,
                              serializers.ModelSerializer):
    """
    used when storing SprayDay objects in Druid
    """
    location_id = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    target_area_id = serializers.SerializerMethodField()
    target_area_name = serializers.SerializerMethodField()
    target_area_structures = serializers.SerializerMethodField()
    rhc_id = serializers.SerializerMethodField()
    rhc_name = serializers.SerializerMethodField()
    rhc_structures = serializers.SerializerMethodField()
    district_id = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    district_structures = serializers.SerializerMethodField()
    sprayoperator_id = serializers.SerializerMethodField()
    sprayoperator_name = serializers.SerializerMethodField()
    sprayoperator_code = serializers.SerializerMethodField()
    team_leader_assistant_id = serializers.SerializerMethodField()
    team_leader_assistant_name = serializers.SerializerMethodField()
    team_leader_id = serializers.SerializerMethodField()
    team_leader_name = serializers.SerializerMethodField()
    geom_lat = serializers.SerializerMethodField()
    geom_lng = serializers.SerializerMethodField()
    sprayed = serializers.SerializerMethodField()
    sprayable = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()
    submission_time = serializers.SerializerMethodField()
    irs_sticker_num = serializers.SerializerMethodField()
    is_new = serializers.SerializerMethodField()
    is_duplicate = serializers.SerializerMethodField()
    is_refused = serializers.SerializerMethodField()
    bgeom_type = serializers.SerializerMethodField()
    bgeom_srid = serializers.SerializerMethodField()
    bgeom_coordinates = serializers.SerializerMethodField()

    class Meta:
        model = SprayDay
        fields = ['submission_id', 'spray_date', 'sprayed', 'reason', 'osmid',
                  'location_id', 'location_name', 'target_area_id',
                  'target_area_name', 'rhc_id', 'rhc_name', 'district_id',
                  'district_name', 'sprayoperator_name', 'sprayoperator_id',
                  'team_leader_assistant_id', 'team_leader_assistant_name',
                  'team_leader_id', 'team_leader_name', 'geom_lat', 'geom_lng',
                  'submission_time', 'is_new', 'target_area_structures',
                  'rhc_structures', 'district_structures', 'sprayable',
                  'is_duplicate', 'is_refused', 'sprayoperator_code',
                  'irs_sticker_num', 'bgeom_type', 'bgeom_coordinates',
                  'bgeom_srid'
                  ]

    def get_sprayoperator_id(self, obj):
        if obj and obj.spray_operator:
            return obj.spray_operator.id

    def get_sprayoperator_name(self, obj):
        if obj and obj.spray_operator:
            return obj.spray_operator.name

    def get_sprayoperator_code(self, obj):
        if obj and obj.spray_operator:
            return obj.spray_operator.code

    def get_team_leader_assistant_id(self, obj):
        if obj and obj.team_leader_assistant:
            return obj.team_leader_assistant.id

    def get_team_leader_assistant_name(self, obj):
        if obj and obj.team_leader_assistant:
            return obj.team_leader_assistant.name

    def get_team_leader_id(self, obj):
        if obj and obj.team_leader:
            return obj.team_leader.id

    def get_team_leader_name(self, obj):
        if obj and obj.team_leader:
            return obj.team_leader.name

    def get_geom_lat(self, obj):
        if obj and obj.geom:
            return obj.geom.coords[1]

    def get_geom_lng(self, obj):
        if obj and obj.geom:
            return obj.geom.coords[0]

    def get_bgeom_type(self, obj):
        if obj and obj.bgeom:
            return "Polygon"

    def get_bgeom_srid(self, obj):
        if obj and obj.bgeom:
            return obj.bgeom.srid

    def get_bgeom_coordinates(self, obj):
        if obj and obj.bgeom:
            return obj.bgeom.tuple

    def get_submission_time(self, obj):
        if obj:
            return obj.data.get('_submission_time')

    def get_sprayable(self, obj):
        if obj:
            sprayable_field = settings.SPRAYABLE_FIELD
            not_sprayable_value = settings.NOT_SPRAYABLE_VALUE
            was_sprayable = obj.data.get(sprayable_field)
            return was_sprayable != not_sprayable_value

    def get_is_new(self, obj):
        if obj:
            osm_new = obj.data.get('osmstructure:node:id', None)
            gps_new = obj.data.get('newstructure/gps', None)
            return any([osm_new, gps_new])

    def get_is_refused(self, obj):
        if obj:
            return obj.data.get(REASON_FIELD, None) is not None

    def get_is_duplicate(self, obj):
        if obj:
            return SprayDay.objects.filter(
                id=obj.id, spraypoint__isnull=True).exists()


class SprayDayDruidBase(object):
    """
    Adds Druid data to Target Area Serializer
    """

    def __init__(self, *args, **kwargs):
        self.druid_data = kwargs.pop('druid_data', None)
        super(SprayDayDruidBase, self).__init__(*args, **kwargs)

    def get_druid_data(self, obj):
        if self.druid_data:
            if isinstance(self.druid_data, list):
                data = [x for x in self.druid_data if x['target_area_id'] ==
                        str(obj.id)]
                if len(data) > 0:
                    return data[0]
            else:
                return self.druid_data
        return None

    def get_district_name(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('district_name')

    def get_district_pk(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('district_id')

    def get_rhc_name(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('rhc_name')

    def get_rhc_pk(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('rhc_id')

    def get_sprayoperator_id(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('sprayoperator_id')

    def get_sprayoperator_name(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('sprayoperator_name')

    def get_sprayoperator_code(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('sprayoperator_code')

    def get_team_leader_assistant_id(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('team_leader_assistant_id')

    def get_team_leader_assistant_name(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('team_leader_assistant_name')

    def get_team_leader_id(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('team_leader_id')

    def get_team_leader_name(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('team_leader_name')

    def get_geom_lat(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('geom_lat')

    def get_geom_lng(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('geom_lng')

    def get_submission_time(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('submission_time')

    def get_sprayed(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('sprayed')

    def get_sprayable(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('sprayable')

    def get_is_new(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('is_new')

    def get_is_refused(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('is_refused')

    def get_is_duplicate(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('is_duplicate')

    def get_total_structures(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('total_structures')

    def get_num_new_structures(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('num_new_no_duplicates', 0)

    def get_found(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('num_found', 0)

    def get_visited_total(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('num_found', 0)

    def get_visited_sprayed(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('num_sprayed', 0)

    def get_visited_not_sprayed(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(
                obj).get('num_not_sprayed_no_duplicates', 0)

    def get_visited_refused(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('num_refused', 0)

    def get_visited_other(self, obj):
        if self.get_druid_data(obj):
            return 0

    def get_not_visited(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('num_not_visited', 0)

    def get_irs_sticker_num(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('irs_sticker_num')

    def get_spray_date(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('spray_date')

    def get_submission_id(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('submission_id')

    def get_reason(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('reason')

    def get_osmid(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('osmid')


class TargetAreaSerializer(SprayDayDruidBase, GeoFeatureModelSerializer):
    """
    Target Area serializer that uses Druid Data
    """
    targetid = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    target_area_name = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    district_pk = serializers.SerializerMethodField()
    rhc_pk = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    structures = serializers.IntegerField()
    total_structures = serializers.SerializerMethodField()
    num_new_structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    spray_dates = serializers.SerializerMethodField()
    geom = GeometryField()

    class Meta:
        fields = ['targetid', 'district_name', 'found', 'url',
                  'structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited', 'bounds', 'spray_dates', 'level',
                  'total_structures', 'district_pk', 'rhc_pk', 'label',
                  'num_new_structures', 'target_area_name']
        model = Location
        geo_field = 'geom'

    def get_targetid(self, obj):
        if obj:
            return obj.id

    def get_target_area_name(self, obj):
        if obj:
            return obj.name

    def get_label(self, obj):
        if obj:
            return obj.name

    def get_url(self, obj):
        return reverse("warehouse:ta", args=[obj.id])

    def get_bounds(self, obj):
        if obj and obj.geom:
            return list(obj.geom.boundary.extent)

    def get_spray_dates(self, obj):
        druid_result = druid_simple_groupby(dimensions=['spray_date'],
                                            filter_list=[['target_area_id',
                                                         operator.eq, obj.id]])
        data = [x['event'] for x in druid_result if x['event']['spray_date']
                is not None]
        return [parser.parse(x['spray_date']).date() for x in data]


class AreaDruidBase(object):
    """
    Adds Druid data extraction to RHC & district serializers
    """

    def __init__(self, *args, **kwargs):
        self.druid_data = kwargs.pop('druid_data', None)
        super(AreaDruidBase, self).__init__(*args, **kwargs)

    def get_druid_data(self, obj):
        if self.druid_data:
            if isinstance(self.druid_data, list):
                data = [x for x in self.druid_data if x['rhc_id'] == obj.id]
                if len(data) > 0:
                    return data[0]
            else:
                return self.druid_data
        return None

    def get_total_structures(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('target_area_count')

    def get_found(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('visited', 0)

    def get_visited_total(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('visited', 0)

    def get_visited_sprayed(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('sprayed', 0)

    def get_visited_not_sprayed(self, obj):
        return 0

    def get_visited_refused(self, obj):
        return 0

    def get_visited_other(self, obj):
        return 0

    def get_not_visited(self, obj):
        return 0


class AreaSerializer(AreaDruidBase, GeoFeatureModelSerializer):
    """
    Used for District & RHC
    """
    targetid = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    structures = serializers.IntegerField()
    total_structures = serializers.SerializerMethodField()
    found = serializers.SerializerMethodField()
    visited_total = serializers.SerializerMethodField()
    visited_sprayed = serializers.SerializerMethodField()
    visited_not_sprayed = serializers.SerializerMethodField()
    visited_refused = serializers.SerializerMethodField()
    visited_other = serializers.SerializerMethodField()
    not_visited = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()
    spray_dates = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    geom = GeometryField()

    class Meta:
        fields = ['targetid', 'found', 'structures', 'visited_total', 'url',
                  'visited_sprayed', 'visited_not_sprayed', 'visited_refused',
                  'visited_other', 'not_visited', 'bounds', 'spray_dates',
                  'level', 'total_structures', 'label']
        model = Location
        geo_field = 'geom'

    def get_targetid(self, obj):
        if obj:
            return obj.id

    def get_label(self, obj):
        if obj:
            return obj.name

    def get_url(self, obj):
        if obj.level == "RHC":
            return reverse("warehouse:rhc_map", args=[obj.id])
        return reverse("warehouse:district_map", args=[obj.id])

    def get_bounds(self, obj):
        if obj and obj.geom:
            return list(obj.geom.boundary.extent)

    def get_spray_dates(self, obj):
        return None

    def get_visited_not_sprayed(self, obj):
        data = self.get_extra_data(obj)
        return data.get('num_not_sprayed_no_duplicates', 0)

    def get_visited_refused(self, obj):
        data = self.get_extra_data(obj)
        return data.get('num_refused', 0)

    def get_extra_data(self, obj):
        data = get_druid_data(dimensions=["rhc_id"],
                              filter_list=[['rhc_id', operator.eq, 14]],
                              order_by=["rhc_id"])
        if len(data) > 0:
            return data[0]['event']
        return {}


class HouseHoldDruidBase(object):

    def __init__(self, *args, **kwargs):
        self.druid_data = kwargs.pop('druid_data', None)
        super(SprayDayDruidBase, self).__init__(*args, **kwargs)

    def get_druid_data(self, obj):
        if self.druid_data:
            if isinstance(self.druid_data, list):
                data = [x for x in self.druid_data if x['id'] == str(obj.id)]
                if len(data) > 0:
                    return data[0]
            else:
                return self.druid_data
        return None

    def get_location_name(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('target_area_name')

    def get_location_id(self, obj):
        if self.get_druid_data(obj):
            return self.get_druid_data(obj).get('target_area_id')
