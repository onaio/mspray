from django.conf import settings
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

from mspray.apps.main.models.spray_day import SprayDay
from mspray.apps.main.models import (
    SprayOperatorDailySummary, DirectlyObservedSprayingForm
)

WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
IRS_NUM_FIELD = settings.MSPRAY_IRS_NUM_FIELD
SPRAY_OPERATOR_NAME = settings.MSPRAY_SPRAY_OPERATOR_NAME
SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE
REASONS = settings.MSPRAY_UNSPRAYED_REASON_OTHER


class SprayBase(object):
    def get_osm_sprayed(self, obj):
        if obj:
            return obj.data.get('osmstructure:spray_status')

    def get_sprayed(self, obj):
        if obj:
            return obj.data.get(WAS_SPRAYED_FIELD)

    def get_reason(self, obj):
        if obj:
            reason = obj.data.get(REASON_FIELD)
            # reason = REASONS.get(reason)
            # if isinstance(reason, str):
            #     reason = reason.lower()

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


class SprayBaseNamibia(SprayBase):
    def get_sprayed(self, obj):
        if obj:
            dm = obj.data.get('sprayed/sprayed_Deltamethrin')
            dm = 0 if dm is None else int(dm)
            ddt = obj.data.get('sprayed/sprayed_DDT')
            ddt = 0 if ddt is None else int(ddt)

            sprayed = 'yes' if ddt + dm > 0 else 'no'

            return sprayed


class SprayDaySerializer(SprayBase, serializers.ModelSerializer):
    sprayed = serializers.SerializerMethodField()
    osm_sprayed = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()
    spray_operator = serializers.SerializerMethodField()
    spray_operator_code = serializers.SerializerMethodField()
    irs_sticker_num = serializers.SerializerMethodField()

    class Meta:
        model = SprayDay
        fields = ('submission_id', 'spray_date', 'sprayed', 'reason', 'osmid',
                  'spray_operator', 'spray_operator_code', 'irs_sticker_num',
                  'osm_sprayed'
                  )


class SprayDayGeoSerializer(SprayBase, GeoFeatureModelSerializer):
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


class SubmissionSerializer(SprayBase, serializers.ModelSerializer):
    spray_area = serializers.SerializerMethodField()
    health_facility = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    class Meta:
        model = SprayDay
        fields = (
            'district', 'health_facility', 'spray_area',
            'osmid', 'was_sprayed', 'submission_id',  'data'
        )

    def get_spray_area(self, obj):
        if obj and obj.location:
            return obj.location.name

    def get_health_facility(self, obj):
        if obj and obj.location and obj.location.parent:
            return obj.location.parent.name

    def get_district(self, obj):
        if obj and obj.location and obj.location.parent \
                and obj.location.parent.parent:
            return obj.location.parent.parent.name

    def get_data(self, obj):
        if obj:
            data = obj.data
            del data['_attachments']
            del data['_bamboo_dataset_id']
            del data['_status']
            del data['_tags']
            del data['_geolocation']

            return data


class SprayDayNamibiaSerializer(SprayBaseNamibia, GeoFeatureModelSerializer):
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
    osm_sprayed = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()
    spray_operator = serializers.SerializerMethodField()
    spray_operator_code = serializers.SerializerMethodField()
    irs_sticker_num = serializers.SerializerMethodField()
    bgeom = GeometryField()

    class Meta:
        model = SprayDay
        fields = ('submission_id', 'spray_date', 'sprayed', 'reason', 'osmid',
                  'spray_operator', 'spray_operator_code', 'irs_sticker_num',
                  'osm_sprayed'
                  )
        geo_field = 'bgeom'


class SprayOperatorDailySerializer(serializers.Serializer):
    spray_form_id = serializers.CharField(max_length=10, required=False)
    sprayed = serializers.IntegerField(required=False)
    found = serializers.IntegerField(required=False)
    sprayoperator_code = serializers.CharField(max_length=10, required=False)

    class Meta:
        model = SprayOperatorDailySummary
        fields = ('spray_form_id', 'sprayed', 'found', 'sprayoperator_code')


class DirectlyObservedSprayingFormSerializer(serializers.Serializer):
    correct_removal = serializers.CharField(max_length=5, required=False)
    correct_mix = serializers.CharField(max_length=5, required=False)
    rinse = serializers.CharField(max_length=5, required=False)
    PPE = serializers.CharField(max_length=5, required=False)
    CFV = serializers.CharField(max_length=5, required=False)
    correct_covering = serializers.CharField(max_length=5, required=False)
    leak_free = serializers.CharField(max_length=5, required=False)
    correct_distance = serializers.CharField(max_length=5, required=False)
    correct_speed = serializers.CharField(max_length=5, required=False)
    correct_overlap = serializers.CharField(max_length=5, required=False)
    district = serializers.CharField(max_length=10, required=False)
    health_facility = serializers.CharField(max_length=50, required=False)
    supervisor_name = serializers.CharField(max_length=10, required=False)
    sprayop_code_name = serializers.CharField(max_length=10, required=False)
    tl_code_name = serializers.CharField(max_length=10, required=False)
    spray_date = serializers.CharField(max_length=10, required=False)

    class Meta:
        model = DirectlyObservedSprayingForm
        fields = (
            'correct_removal', 'correct_mix', 'rinse', 'PPE', 'CFV',
            'correct_covering', 'leak_free', 'correct_distance',
            'correct_speed', 'correct_overlap', 'district', 'health_facility',
            'supervisor_name', 'sprayop_code_name', 'tl_code_name',
            'spray_date'
        )
