from rest_framework import serializers


class DistrictSerializer(serializers.Serializer):
    district_name = serializers.CharField(max_length=255)
    num_target_areas = serializers.IntegerField()
