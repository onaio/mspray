# -*- coding -*-
"""Trials models."""
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class Sample(models.Model):
    """Sample model stores all collected samples"""
    CDC_LIGHT_TRAP = 'CDC Light Trap'
    PROKOPACK = 'Prokopack'

    COLLECTION_METHODS = (
        (CDC_LIGHT_TRAP, 'CDC Light Trap'),
        (PROKOPACK, 'Prokopack'),
    )

    district = models.ForeignKey(
        'main.Location',
        on_delete=models.CASCADE,
        related_name='district_samples')
    spray_area = models.ForeignKey(
        'main.Location',
        on_delete=models.CASCADE,
        related_name='spray_area_samples')
    household_id = models.CharField(max_length=10)
    collection_method = models.CharField(
        max_length=20, choices=COLLECTION_METHODS)
    sample_date = models.DateField()
    visit = models.PositiveSmallIntegerField()
    data = JSONField()
    submission_id = models.PositiveIntegerField(unique=True)
    geom = models.GeometryField(srid=4326, db_index=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
