from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class Node(models.Model):
    node_id = models.BigIntegerField(unique=True)
    version = models.IntegerField()
    changeset = models.IntegerField()
    user = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(null=True)
    geom = models.PointField(srid=4326, null=True)
    tags = JSONField(default={}, null=True)

    class Meta:
        app_label = 'main'


class Way(models.Model):
    way_id = models.BigIntegerField(unique=True)
    action = models.CharField(max_length=20, null=True)
    version = models.IntegerField()
    changeset = models.IntegerField()
    user = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(null=True)
    geom = models.PolygonField(srid=4326, null=True)
    tags = JSONField(default={}, null=True)

    class Meta:
        app_label = 'main'
