# -*- coding=utf-8 -*-
"""
sync_missing_data command.
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.utils import sync_missing_sprays

FORMID = getattr(settings, 'ONA_FORM_PK', 0)


class Command(BaseCommand):
    """
    sync_missing_data command - fetches unsynced data from Ona for given form.
    """
    help = _('Fetch data from ona server.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--formid',
            dest='formid',
            default=FORMID,
            type=int,
            help='form id')

    def handle(self, *args, **options):
        formid = int(options['formid']) if 'formid' in options else FORMID

        if formid != 0:
            sync_missing_sprays(formid, self.stdout.write)
        else:
            self.stdout.write("Missing or Invalid formid {}".format(formid))
