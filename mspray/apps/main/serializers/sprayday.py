from django.conf import settings
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

from mspray.apps.main.models.spray_day import SprayDay

WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
IRS_NUM_FIELD = settings.MSPRAY_IRS_NUM_FIELD
SPRAY_OPERATOR_NAME = settings.MSPRAY_SPRAY_OPERATOR_NAME
SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE
REASONS = settings.MSPRAY_UNSPRAYED_REASON_OTHER


class SprayBase(object):
    def get_sprayed(self, obj):
        if obj:
            return obj.data.get(WAS_SPRAYED_FIELD)

    def get_reason(self, obj):
        if obj:
            reason = obj.data.get(REASON_FIELD)
            reason = REASONS.get(reason)
            if isinstance(reason, str):
                reason = reason.lower()

            return reason

    def get_spray_operator(self, obj):
        if obj:
            return obj.data.get(SPRAY_OPERATOR_NAME)

    def get_spray_operator_code(self, obj):
        if obj:
            return obj.data.get(SPRAY_OPERATOR_CODE)

    def get_irs_sticker_num(self, obj):
        if obj:
            return obj.data.get(IRS_NUM_FIELD)


class SprayDaySerializer(SprayBase, GeoFeatureModelSerializer):
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


class SprayDayShapeSerializer(SprayBase, GeoFeatureModelSerializer):
    sprayed = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()
    spray_operator = serializers.SerializerMethodField()
    spray_operator_code = serializers.SerializerMethodField()
    irs_sticker_num = serializers.SerializerMethodField()
    bgeom = GeometryField()

    class Meta:
        model = SprayDay
        fields = ('submission_id', 'spray_date', 'sprayed', 'reason',
                  'spray_operator', 'spray_operator_code', 'irs_sticker_num')
        geo_field = 'bgeom'
