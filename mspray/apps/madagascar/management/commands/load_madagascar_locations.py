import codecs
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import District
from mspray.apps.main.models import TargetArea


class Command(BaseCommand):
    args = '<path to shapefile>'
    help = _('Load madagascar locations')

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError(_('Missing locations csv file path'))
        for path in args:
            try:
                path = os.path.abspath(path)
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                structures_targeted = 'Structures Targeted'
                commune = 'Commune'
                fokontany = 'Fokontany'

                with codecs.open(path, encoding='utf-8') as f:
                    csv_reader = csv.DictReader(f)
                    for row in csv_reader:
                        structures = int(row[structures_targeted])
                        district, created = District.objects.get_or_create(
                            district_name=row[commune],
                            code=row[commune]
                        )
                        ta, ta_created = TargetArea.objects.get_or_create(
                            district=district,
                            targetid=row[fokontany],
                            district_name=row[commune],
                            houses=structures
                        )
                        if ta_created:
                            district.houses = district.houses + structures
                            district.save()

                            print(row)
