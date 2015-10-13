from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from mspray.apps.main.models import SprayDay
from mspray.apps.main.utils import get_spray_operator
from mspray.apps.main.utils import get_team_leader
SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE
TEAM_LEADER_CODE = settings.MSPRAY_TEAM_LEADER_CODE


class Command(BaseCommand):
    help = _('Link spray operator ans team leader to spray data.')

    def handle(self, *args, **options):
        unlinked = SprayDay.objects.filter(spray_operator=None)
        count = unlinked.count()
        for sprayday in unlinked.iterator():

            so = get_spray_operator(sprayday.data.get(SPRAY_OPERATOR_CODE))
            if so:
                sprayday.spray_operator = so

            team_leader = get_team_leader(sprayday.data.get(TEAM_LEADER_CODE))
            if team_leader:
                sprayday.team_leader = team_leader

            if so or team_leader:
                sprayday.save()

        self.stdout.write("{} linked of {}.".format(
            count - SprayDay.objects.filter(spray_operator=None).count(), count
        ))
