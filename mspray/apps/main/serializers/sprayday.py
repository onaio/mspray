from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.main.models.spray_day import SprayDay


class SprayDaySerializer(GeoFeatureModelSerializer):
    sprayed = serializers.SerializerMethodField('get_sprayed')
    reason = serializers.SerializerMethodField('get_reason')
    spray_operator = serializers.SerializerMethodField('get_spray_operator')
    spray_operator_code = serializers.SerializerMethodField(
        'get_spray_operator_code')
    irs_sticker_num = serializers.SerializerMethodField('get_irs_sticker_num')

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
            return obj.data.get('unsprayed/reason')

    def get_spray_operator(self, obj):
        if obj:
            return obj.data.get('sprayed/spray_operator_name')

    def get_spray_operator_code(self, obj):
        if obj:
            return obj.data.get('sprayed/spray_operator_code')

    def get_irs_sticker_num(self, obj):
        if obj:
            return obj.data.get('irs_sticker_num')
