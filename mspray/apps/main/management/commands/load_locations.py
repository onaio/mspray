import codecs
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location


class Command(BaseCommand):
    args = '<path to shapefile>'
    help = _('Load locations')

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError(_('Missing locations csv file path'))
        for path in args:
            try:
                path = os.path.abspath(path)
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                code = 'code'
                level = 'level'
                name = 'name'
                structures_targeted = 'structures'
                count = Location.objects.count()

                with codecs.open(path, encoding='utf-8') as f:
                    csv_reader = csv.DictReader(f)
                    for row in csv_reader:
                        try:
                            structures = int(row[structures_targeted])
                        except ValueError:
                            structures = 0

                        parent = row['parent'].strip()
                        parent_loc = None
                        if parent != '' and parent is not None:
                            parent_loc = Location.objects.get(code=parent)

                        location, created = Location.objects.get_or_create(
                            name=row[name].strip(),
                            code=row[code].strip(),
                            level=row[level].strip(),
                            parent=parent_loc,
                            structures=structures
                        )

                print("Created {} locations".format(
                    Location.objects.count() - count))
