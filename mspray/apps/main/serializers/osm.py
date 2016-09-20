from rest_framework import serializers

from mspray.apps.main.models import Way


class OsmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Way
