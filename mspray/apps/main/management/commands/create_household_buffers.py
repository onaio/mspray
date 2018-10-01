# -*- coding: utf-8  -*-
"""
Create household buffers.
"""
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main import utils
from mspray.apps.main.models.households_buffer import HouseholdsBuffer


class Command(BaseCommand):
    """
    create_household_buffers command.
    """
    help = _("Create Household buffers.")

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--distance", default=15, dest="distance", type=float
        )
        parser.add_argument("-f", "--force", default=False, dest="recreate")
        parser.add_argument("-t", "--target", default=False, dest="target")

    def handle(self, *args, **options):
        distance = options.get("distance")
        recreate = options.get("recreate")
        target = options.get("target")
        count = HouseholdsBuffer.objects.count()

        utils.create_households_buffer(
            distance=distance, recreate=recreate, target=target
        )

        after_count = HouseholdsBuffer.objects.count()

        print("before: %d Buffers" % count)
        print("after: %d Buffers" % after_count)
