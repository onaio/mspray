# -*- coding=utf-8 -*-
"""
Link new structures to existing households
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location
from mspray.apps.main.utils import link_new_structures_to_existing


class Command(BaseCommand):
    """
    Link new structures to existing households within a target area

    This is done by checking if the new point is close to any existing
    structure and then attaching that new point to that existing structure
    """

    help = _("Link new structures to existing households in a target area")

    def add_arguments(self, parser):
        """Command arguments"""
        parser.add_argument(
            "location_id", type=int, help=_("The location_id.")
        )

    def handle(self, *args, **options):
        """
        Actually do the work!
        """
        try:
            pk = options["location_id"]
        except KeyError:
            raise CommandError(_("Please specify field to use."))
        else:
            try:
                location = Location.objects.get(pk=int(pk))
            except Location.DoesNotExist:
                raise CommandError(_("Location does not exist."))
            else:
                link_new_structures_to_existing(target_area=location)
