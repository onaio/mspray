import os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.osm import add_or_update_osm_data


class Command(BaseCommand):
    help = _(
        """
Load osm data from osm files. The following is an example of how it's used:
python manage.py load_osm_data -p "data/zambia/osm_files" --settings=local_settings
"""  # noqa
    )
    option_list = BaseCommand.option_list + (
        make_option('-p', '--path', default=False, dest='path'),
    )

    def handle(self, *args, **options):
        path = options.get('path')
        osm_files = os.listdir(path)

        if len(osm_files) != 0:
            for a in osm_files:
                file_path = "%s/%s" % (path, a)
                add_or_update_osm_data(file_path)

                print("Done with file %s" % file_path)
