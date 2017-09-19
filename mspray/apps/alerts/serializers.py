from django.contrib.gis.geos import Point

from rest_framework import serializers

from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.serializers import mSpraySerializer


class UserDistanceSerializer(mSpraySerializer):
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

