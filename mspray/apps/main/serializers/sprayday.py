from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

from mspray.apps.main.models.spray_day import SprayDay


class SprayDaySerializer(GeoFeatureModelSerializer):
    sprayed = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()
    spray_operator = serializers.SerializerMethodField()
    spray_operator_code = serializers.SerializerMethodField()
    irs_sticker_num = serializers.SerializerMethodField()
    geom = GeometryField()

    class Meta:
        model = SprayDay
        fields = ('submission_id', 'spray_date', 'sprayed', 'reason',
                  'spray_operator', 'spray_operator_code', 'irs_sticker_num')
        geo_field = 'geom'

    def get_sprayed(self, obj):
        if obj:
            return obj.data.get('sprayed/was_sprayed')

    def get_reason(self, obj):
        if obj:
            reason = obj.data.get('unsprayed/reason')
            if isinstance(reason, str):
                reason = reason.lower()

            return reason

    def get_spray_operator(self, obj):
        if obj:
            return obj.data.get('sprayed/sprayop_name')

    def get_spray_operator_code(self, obj):
        if obj:
            return obj.data.get('sprayed/sprayop_code')

    def get_irs_sticker_num(self, obj):
        if obj:
            return obj.data.get('irs_sticker_num')
