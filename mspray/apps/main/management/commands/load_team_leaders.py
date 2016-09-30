import codecs
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from mspray.apps.main.models import Location
from mspray.apps.main.models import TeamLeader


class Command(BaseCommand):
    args = '<path to team leaders csv with columns code|name>'
    help = _('Load team leaders')

    def add_arguments(self, parser):
        parser.add_argument('csv_file', metavar="FILE")

    def handle(self, *args, **options):
        if 'csv_file' not in options:
            raise CommandError(_('Missing team leaders csv file path'))
        else:
            try:
                path = os.path.abspath(options['csv_file'])
            except Exception as e:
                raise CommandError(_('Error: %(msg)s' % {"msg": e}))
            else:
                with codecs.open(path, encoding='utf-8') as f:
                    csv_reader = csv.DictReader(f)
                    for row in csv_reader:
                        team_leader, created = \
                            TeamLeader.objects.get_or_create(
                                code=row['code'].strip(),
                                name=row['name']
                            )
                        if created:
                            print(row)
                        district = row['district'].strip()
                        if district:
                            location = Location.objects.get(code=district,
                                                            level='district')
                            team_leader.location = location
                            team_leader.save()
