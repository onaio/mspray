import codecs
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayOperator


class Command(BaseCommand):
    args = '<path to spray operators csv with columns code|name>'
    help = _('Load spray operators')

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError(_('Missing csv file path'))
        for path in args:
            try:
                path = os.path.abspath(path)
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                with codecs.open(path, encoding='utf-8') as f:
                    csv_reader = csv.DictReader(f)
                    for row in csv_reader:
                        spray_operator, created = \
                            SprayOperator.objects.get_or_create(
                                code=int(row['code']),
                                name=row['name']
                            )
                        if created:
                            print(row)