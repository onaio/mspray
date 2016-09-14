from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class Node(models.Model):
    node_id = models.CharField(unique=True, max_length=25)
    version = models.IntegerField()
    changeset = models.IntegerField()
    user = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(null=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    tags = JSONField(default={}, null=True)

    class Meta:
        app_label = 'main'


class Way(models.Model):
    way_id = models.CharField(unique=True, max_length=25)
    action = models.CharField(max_length=20, null=True)
    version = models.IntegerField()
    changeset = models.IntegerField()
    user = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(null=True)
    nd_path = models.CharField(max_length=255, null=True)
    tags = JSONField(default={}, null=True)

    class Meta:
        app_label = 'main'
