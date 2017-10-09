from django.test import TestCase
from django.core.management import call_command
from django.conf import settings


class TestBase(TestCase):

    def _load_fixtures(self):
        call_command(
            'loaddata', settings.BASE_DIR + '/mspray/apps/main/tests/fixtures'
            '/20171009/location.json', verbosity=0)
        call_command(
            'loaddata', settings.BASE_DIR + '/mspray/apps/main/tests/fixtures'
            '/20171009/team_leader.json', verbosity=0)
        call_command(
            'loaddata', settings.BASE_DIR + '/mspray/apps/main/tests/fixtures'
            '/20171009/team_leader_assistant.json', verbosity=0)
        call_command(
            'loaddata', settings.BASE_DIR + '/mspray/apps/main/tests/fixtures'
            '/20171009/spray_operator.json', verbosity=0)
        call_command(
            'loaddata', settings.BASE_DIR + '/mspray/apps/main/tests/fixtures'
            '/20171009/sprayday.json', verbosity=0)
        call_command(
            'loaddata', settings.BASE_DIR + '/mspray/apps/main/tests/fixtures'
            '/20171009/spraypoint.json', verbosity=0)
        call_command(
            'loaddata', settings.BASE_DIR + '/mspray/apps/main/tests/fixtures'
            '/20171009/household.json', verbosity=0)
