from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import Hhcsv
from mspray.apps.main.models import OsmData
from mspray.apps.main.models import MatchedData
SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE
TEAM_LEADER_CODE = settings.MSPRAY_TEAM_LEADER_CODE


class Command(BaseCommand):
    help = _('Link spray operator ans team leader to spray data.')

    def handle(self, *args, **options):
        osm_data = OsmData.objects.filter()
        count = osm_data.count()
        matched = 0
        unmatched = 0
        multimatched = 0
        k = 0
        for osm in osm_data.iterator():
            match = Hhcsv.objects.filter(
                shape_area=osm.shape_area,
                shape_length=osm.shape_length
            ).count()
            k += 1
            if match == 1:
                matched += 1
                rec = Hhcsv.objects.filter(
                    shape_area=osm.shape_area,
                    shape_length=osm.shape_length
                ).first()
                MatchedData.objects.create(
                    building=osm.building,
                    osmpk=osm.pk,
                    osmid=osm.osmid,
                    y=rec.y,
                    x3=rec.x3,
                    district=osm.district,
                    target_area=osm.target_area,
                    shape_area=osm.shape_area,
                    shape_length=osm.shape_length
                )
            elif match > 1:
                multimatched += 1
            else:
                unmatched += 1

            if k % 2000 == 0:
                self.stdout.write(
                    "{} matched, {} multimatched, {} unmatched of {}.".format(
                        matched, multimatched, unmatched, k
                    )
                )

        self.stdout.write(
            "{} matched, {} multimatched, {} unmatched of {}.".format(
                matched, multimatched, unmatched, count
            )
        )
