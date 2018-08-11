# -*- coding: utf-8 -*-
"""Trials serializers.
"""
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from mspray.apps.trials.models import Sample


class GeoSamplesSerializer(GeoFeatureModelSerializer):
    """Samples Serializer for geojson data.
    """
    geom = GeometryField()
    samples = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'household_id', 'samples')
        model = Sample
        geo_field = 'geom'

    def get_samples(self, obj):  # pylint: disable=no-self-use
        """Return sample data for the current household_id.
        """
        samples = Sample.objects.filter(household_id=obj.household_id)\
            .order_by('visit', 'sample_date').values_list('data', flat=True)

        return [sample for sample in samples]
