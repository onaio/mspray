from django.contrib.gis.geos import Point

from rest_framework import serializers

from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer


class RapidProBaseSerializer(serializers.Serializer):
    """
    Prepares druid data to send to RapidPro
    """
    target_area_id = serializers.IntegerField()
    target_area_name = serializers.CharField()
    rhc_id = serializers.IntegerField()
    rhc_name = serializers.CharField()
    district_id = serializers.IntegerField()
    district_name = serializers.CharField()
    num_found = serializers.IntegerField(default=0)
    num_sprayed = serializers.IntegerField(default=0)
    spray_coverage = serializers.IntegerField(default=0)
    found_coverage = serializers.IntegerField(default=0)
    spray_effectiveness = serializers.IntegerField(default=0)
    total_structures = serializers.IntegerField(default=0)
    date = serializers.SerializerMethodField()

    def get_date(self, obj):
        if self.date:
            return self.date

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop('date', None)
        super(RapidProBaseSerializer, self).__init__(*args, **kwargs)


class FoundCoverageSerializer(RapidProBaseSerializer):
    """
    Prepares druid data to send to RapidPro
    """
    target_area_id = serializers.SerializerMethodField()
    target_area_name = serializers.SerializerMethodField()
    rhc_id = serializers.SerializerMethodField()
    rhc_name = serializers.SerializerMethodField()
    district_id = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    has_submissions_today = serializers.IntegerField(default=0)
    today_is_working_day = serializers.IntegerField(default=0)
    total_structures = serializers.SerializerMethodField(default=0)

    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop('date', None)
        self.target_area = kwargs.pop('target_area', None)
        super(RapidProBaseSerializer, self).__init__(*args, **kwargs)

    def get_target_area_id(self, data):
        if data.get('target_area_id'):
            return data['target_area_id']
        if self.target_area:
            return self.target_area.id

    def get_target_area_name(self, data):
        if data.get('target_area_name'):
            return data['target_area_name']
        if self.target_area:
            return self.target_area.name

    def get_rhc_id(self, data):
        if data.get('rhc_id'):
            return data['rhc_id']
        if self.target_area:
            return self.target_area.parent.id

    def get_rhc_name(self, data):
        if data.get('rhc_name'):
            return data['rhc_name']
        if self.target_area:
            return self.target_area.parent.name

    def get_district_id(self, data):
        if data.get('district_id'):
            return data['district_id']
        if self.target_area:
            return self.target_area.parent.parent.id

    def get_district_name(self, data):
        if data.get('district_name'):
            return data['district_name']
        if self.target_area:
            return self.target_area.parent.parent.name

    def get_total_structures(self, data):
        if data.get('total_structures'):
            return data['total_structures']
        if self.target_area:
            return self.target_area.structures


class UserDistanceSerializer(SprayDayDruidSerializer):
    """
    Serliazer for SpraDay object that calculates field between structure
    and user
    """
    target_area_id = serializers.SerializerMethodField()
    target_area_name = serializers.SerializerMethodField()
    rhc_id = serializers.SerializerMethodField()
    rhc_name = serializers.SerializerMethodField()
    district_id = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    sprayoperator_name = serializers.SerializerMethodField()
    sprayoperator_code = serializers.SerializerMethodField()
    team_leader_assistant_name = serializers.SerializerMethodField()
    team_leader_name = serializers.SerializerMethodField()
    user_latlng = serializers.SerializerMethodField()
    structure_latlng = serializers.SerializerMethodField()
    distance_from_structure = serializers.SerializerMethodField()

    class Meta:
        model = SprayDay
        fields = ['target_area_id', 'target_area_name', 'rhc_id', 'rhc_name',
                  'district_id', 'district_name', 'sprayoperator_name',
                  'sprayoperator_code', 'team_leader_assistant_name',
                  'team_leader_name', 'user_latlng', 'structure_latlng',
                  'distance_from_structure']

    def get_user_latlng(self, obj):
        if obj and obj.data.get('osmstructure:userlatlng'):
            return obj.data.get('osmstructure:userlatlng')

    def get_structure_latlng(self, obj):
        if obj and obj.geom:
            return "{},{}".format(obj.geom.coords[1], obj.geom.coords[0])

    def get_distance_from_structure(self, obj):
        if obj and obj.geom and obj.data.get('osmstructure:userlatlng'):
            latlong = [float(x) for x in
                       obj.data.get('osmstructure:userlatlng').split(",")]
            user_location = Point(latlong[1], latlong[0])
            return int(user_location.distance(obj.geom))

