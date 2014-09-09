from django.core.management import call_command
from mspray.apps.main.models.households_buffer import HouseholdsBuffer

from mspray.apps.main.tests.test_base import TestBase


class TestCreateHouseholdBuffers(TestBase):
    def test_create_household_buffers(self):
        count = HouseholdsBuffer.objects.count()
        self._loaddata_fixtures(['848_target_area', '848_households'])

        call_command('create_household_buffers')
        self.assertEqual(HouseholdsBuffer.objects.count(), count + 23)

        call_command('create_household_buffers', distance=10, recreate=True)
        self.assertEqual(HouseholdsBuffer.objects.count(), count + 97)
