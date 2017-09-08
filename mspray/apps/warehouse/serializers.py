from rest_framework import serializers

from mspray.apps.main.models import SprayDay
from mspray.apps.main.serializers.sprayday import SprayBase


def get_location_tree(location):
    """
    takes a location object and returns a dict
    with the full location tree
    """


class mSpraySerializer(SprayBase, serializers.ModelSerializer):
    """
    Creates a de-normalised record that will be fed into Druid
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
    is_new = serializers.SerializerMethodField()
    is_duplicate = serializers.SerializerMethodField()

    class Meta:
        model = SprayDay
        fields = ('submission_id', 'spray_date', 'sprayed', 'reason', 'osmid',
                  'location_id', 'location_name', 'target_area_id',
                  'target_area_name', 'rhc_id', 'rhc_name', 'district_id',
                  'district_name', 'sprayoperator_name', 'sprayoperator_id',
                  'team_leader_assistant_id', 'team_leader_assistant_name',
                  'team_leader_id', 'team_leader_name', 'geom_lat', 'geom_lng',
                  'submission_time', 'is_new', 'target_area_structures',
                  'rhc_structures', 'district_structures', 'sprayable',
                  'is_duplicate'
                  )

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

    def get_sprayoperator_id(self, obj):
        if obj and obj.spray_operator:
            return obj.spray_operator.id

    def get_sprayoperator_name(self, obj):
        if obj and obj.spray_operator:
            return obj.spray_operator.name

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

    def get_submission_time(self, obj):
        if obj:
            return obj.data.get('_submission_time')

    def get_sprayable(self, obj):
        if obj:
            return obj.data.get('sprayable_structure')

    def get_is_new(self, obj):
        if obj:
            osm_new = obj.data.get('osmstructure:node:id', None)
            gps_new = obj.data.get('newstructure/gps', None)
            return any([osm_new, gps_new])

    def get_is_duplicate(self, obj):
        if obj:
            return SprayDay.objects.filter(
                id=obj.id, spraypoint__isnull=True).exists()
