"""Reactive IRS model"""

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext as _

SRID = settings.MSPRAY_DEFAULT_SRID


class CommunityHealthWorker(models.Model):
    """Model definition for CommunityHealthWorker."""

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    geom = models.PointField(srid=SRID)
    bgeom = models.GeometryField(srid=SRID, null=True)
    location = models.ForeignKey(
        "main.Location",
        related_name="chw",
        null=True,
        on_delete=models.CASCADE)

    class Meta:
        """Meta definition for CommunityHealthWorker."""

        verbose_name = _("Community Health Worker")
        verbose_name_plural = _("Community Health Workers")

    def __str__(self):
        """Unicode representation of CommunityHealthWorker."""
        return self.name
