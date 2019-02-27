"""Reactive IRS model"""

from django.contrib.gis.db import models
from django.utils.translation import ugettext as _


class CommunityHealthWorker(models.Model):
    """Model definition for CommunityHealthWorker."""

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, db_index=True)
    geom = models.PointField(srid=4326, db_index=True, null=False)
    bgeom = models.GeometryField(srid=4326, db_index=True, null=True)
    location = models.ForeignKey(
        "main.Location", related_name="chw", db_index=True, null=True,
        on_delete=models.CASCADE)

    class Meta:
        """Meta definition for CommunityHealthWorker."""

        verbose_name = _("Community Health Worker")
        verbose_name_plural = _("Community Health Workers")

    def __str__(self):
        """Unicode representation of CommunityHealthWorker."""
        return self.name
