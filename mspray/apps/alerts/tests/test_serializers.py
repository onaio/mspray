from django.conf import settings

from rest_framework.utils.serializer_helpers import ReturnDict

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.alerts.serializers import GPSSerializer


class TestSerializers(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self._load_fixtures()

    def test_gpsserializer(self):
        """
        Ensure that GPSSerializer returns exactly the data that
        we expect
        """
        sprayday = SprayDay.objects.first()
        expected_keys = ['target_area_id', 'target_area_name', 'rhc_id',
                         'rhc_name', 'district_id', 'district_name',
                         'sprayoperator_name', 'sprayoperator_code',
                         'team_leader_assistant_name', 'team_leader_name',
                         'gps_on', 'district_code']

        this_rhc = sprayday.location.get_family().filter(level='RHC').first()
        this_district = sprayday.location.get_family().filter(
                            level='district').first()

        if settings.MSPRAY_USER_LATLNG_FIELD in sprayday.data:
            gps_on = 1
        else:
            gps_on = 0

        serialized = GPSSerializer(sprayday).data
        self.assertTrue(isinstance(serialized, ReturnDict))
        received_keys = serialized.keys()
        self.assertEqual(len(received_keys), len(expected_keys))
        for key in received_keys:
            self.assertTrue(key in expected_keys)
        self.assertEqual(serialized['target_area_id'], sprayday.location.id)
        self.assertEqual(serialized['target_area_name'],
                         sprayday.location.name)
        self.assertEqual(serialized['rhc_id'], this_rhc.id)
        self.assertEqual(serialized['rhc_name'], this_rhc.name)
        self.assertEqual(serialized['district_id'], this_district.id)
        self.assertEqual(serialized['district_name'], this_district.name)
        self.assertEqual(serialized['district_code'], this_district.code)
        self.assertEqual(serialized['sprayoperator_code'],
                         sprayday.spray_operator.code)
        self.assertEqual(serialized['sprayoperator_name'],
                         sprayday.spray_operator.name)
        if sprayday.team_leader_assistant:
            self.assertEqual(serialized['team_leader_assistant_name'],
                             sprayday.team_leader_assistant.name)
        else:
            self.assertEqual(serialized['team_leader_assistant_name'], None)
        if sprayday.team_leader:
            self.assertEqual(serialized['team_leader_name'],
                             sprayday.team_leader.name)
        else:
            self.assertEqual(serialized['team_leader_name'], None)
        self.assertEqual(serialized['gps_on'], gps_on)
