"""Reactive IRS signals module"""

from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from mspray.apps.reactive.irs.models import CommunityHealthWorker
from mspray.apps.reactive.irs.utils import get_chw_location


@receiver(
    pre_save,
    sender=CommunityHealthWorker,
    dispatch_uid="populate_bgeom_field")
def populate_bgeom_field(
        sender: object, instance: object,
        **kwargs):  # pylint: disable=unused-argument
    """Populate bgeom field using geom and a buffer"""

    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance.bgeom = instance.geom.buffer(
            settings.MSPRAY_REACTIVE_IRS_CHW_BUFFER, 1)
    else:
        if not obj.bgeom == instance.bgeom:  # Field has changed
            instance.bgeom = instance.geom.buffer(
                settings.MSPRAY_REACTIVE_IRS_CHW_BUFFER, 1)


@receiver(
    pre_save,
    sender=CommunityHealthWorker,
    dispatch_uid="connect_chw_location")
def connect_chw_location(
        sender: object, instance: object,
        **kwargs):  # pylint: disable=unused-argument
    """Connect CHW to location"""
    if settings.MSPRAY_REACTIVE_IRS_CREATE_CHW_LOCATION:
        location = get_chw_location(chw=instance)

        if instance.location != location:
            instance.location = location
