from django.conf import settings

from rest_framework.utils.serializer_helpers import ReturnDict
from dateutil import parser

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay
from mspray.apps.warehouse.serializers import SprayDayDruidSerializer

REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
NEW_WAS_SPRAYED_FIELD = settings.MSPRAY_NEW_STRUCTURE_WAS_SPRAYED_FIELD
IRS_NUM_FIELD = settings.MSPRAY_IRS_NUM_FIELD


class TestSerializers(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self._load_fixtures()

    def test_spraydaydruidserializer(self):
        """
        Ensure that SprayDayDruidSerializer returns exactly the data that
        we expect
        """
        sprayday = SprayDay.objects.first()
        expected_keys = ['submission_id', 'spray_date', 'sprayed', 'reason',
                         'osmid', 'location_id', 'location_name',
                         'target_area_id', 'target_area_name', 'rhc_id',
                         'rhc_name', 'district_id', 'district_name',
                         'sprayoperator_name', 'sprayoperator_id',
                         'team_leader_assistant_id',
                         'team_leader_assistant_name', 'team_leader_id',
                         'team_leader_name', 'geom_lat', 'geom_lng',
                         'submission_time', 'is_new', 'target_area_structures',
                         'rhc_structures', 'district_structures', 'sprayable',
                         'is_duplicate', 'is_refused', 'sprayoperator_code',
                         'irs_sticker_num', 'bgeom_type', 'bgeom_coordinates',
                         'bgeom_srid', 'team_leader_code', 'district_code',
                         'rhc_code', 'target_area_code', 'timestamp',
                         'team_leader_assistant_code']
        # was sprayed
        if sprayday.data.get(NEW_WAS_SPRAYED_FIELD):
            was_sprayed_field = NEW_WAS_SPRAYED_FIELD
        elif sprayday.data.get(WAS_SPRAYED_FIELD):
            was_sprayed_field = WAS_SPRAYED_FIELD
        # sprayable
        sprayable_field = None

        if sprayday.data.get(settings.NEW_STRUCTURE_SPRAYABLE_FIELD):
            sprayable_field = settings.NEW_STRUCTURE_SPRAYABLE_FIELD
        elif sprayday.data.get(settings.SPRAYABLE_FIELD):
            sprayable_field = settings.SPRAYABLE_FIELD

        not_sprayable_value = settings.NOT_SPRAYABLE_VALUE
        was_sprayable = sprayday.data.get(sprayable_field)
        sprayable = was_sprayable != not_sprayable_value
        # new
        osm_new = sprayday.data.get('osmstructure:node:id', None)
        gps_new = sprayday.data.get('newstructure/gps', None)
        is_new = any([osm_new, gps_new])
        # refused
        is_refused = sprayday.data.get(REASON_FIELD, None) is not None
        # duplicate
        is_duplicate = SprayDay.objects.filter(
                        id=sprayday.id, spraypoint__isnull=True).exists()

        this_rhc = sprayday.location.get_family().filter(level='RHC').first()
        this_district = sprayday.location.get_family().filter(
                            level='district').first()
        # timestamp
        timestamp = parser.parse(sprayday.data.get('end')).isoformat()

        serialized = SprayDayDruidSerializer(sprayday).data

        self.assertTrue(isinstance(serialized, ReturnDict))
        received_keys = serialized.keys()
        self.assertEqual(len(received_keys), len(expected_keys))
        for key in received_keys:
            self.assertTrue(key in expected_keys)
        self.assertEqual(serialized['location_id'], sprayday.location.id)
        self.assertEqual(serialized['location_name'], sprayday.location.name)
        self.assertEqual(serialized['target_area_id'], sprayday.location.id)
        self.assertEqual(serialized['target_area_code'],
                         sprayday.location.code)
        self.assertEqual(serialized['target_area_name'],
                         sprayday.location.name)
        self.assertEqual(serialized['target_area_structures'],
                         sprayday.location.structures)
        self.assertEqual(serialized['rhc_id'], this_rhc.id)
        self.assertEqual(serialized['rhc_code'], this_rhc.code)
        self.assertEqual(serialized['rhc_name'], this_rhc.name)
        self.assertEqual(serialized['rhc_structures'], this_rhc.structures)
        self.assertEqual(serialized['district_id'], this_district.id)
        self.assertEqual(serialized['district_name'], this_district.name)
        self.assertEqual(serialized['district_code'], this_district.code)
        self.assertEqual(serialized['district_structures'],
                         this_district.structures)
        self.assertEqual(serialized['sprayoperator_id'],
                         sprayday.spray_operator.id)
        self.assertEqual(serialized['sprayoperator_name'],
                         sprayday.spray_operator.name)
        self.assertEqual(serialized['sprayoperator_code'],
                         sprayday.spray_operator.code)
        if sprayday.team_leader_assistant:
            self.assertEqual(serialized['team_leader_assistant_id'],
                             sprayday.team_leader_assistant.id)
            self.assertEqual(serialized['team_leader_assistant_code'],
                             sprayday.team_leader_assistant.code)
            self.assertEqual(serialized['team_leader_assistant_name'],
                             sprayday.team_leader_assistant.name)
        else:
            self.assertEqual(serialized['team_leader_assistant_id'], None)
            self.assertEqual(serialized['team_leader_assistant_code'], None)
            self.assertEqual(serialized['team_leader_assistant_name'], None)
        if sprayday.team_leader:
            self.assertEqual(serialized['team_leader_id'],
                             sprayday.team_leader.id)
            self.assertEqual(serialized['team_leader_code'],
                             sprayday.team_leader.code)
            self.assertEqual(serialized['team_leader_name'],
                             sprayday.team_leader.name)
        else:
            self.assertEqual(serialized['team_leader_id'], None)
            self.assertEqual(serialized['team_leader_code'], None)
            self.assertEqual(serialized['team_leader_name'], None)
        self.assertEqual(serialized['geom_lat'], sprayday.geom.coords[1])
        self.assertEqual(serialized['geom_lng'], sprayday.geom.coords[0])
        self.assertEqual(serialized['sprayed'],
                         sprayday.data.get(was_sprayed_field))
        self.assertEqual(serialized['sprayable'], sprayable)
        self.assertEqual(serialized['reason'], sprayday.data.get(REASON_FIELD))
        self.assertEqual(serialized['submission_time'],
                         sprayday.data.get('_submission_time'))
        self.assertEqual(serialized['irs_sticker_num'],
                         sprayday.data.get(IRS_NUM_FIELD))
        self.assertEqual(serialized['is_new'], is_new)
        self.assertEqual(serialized['timestamp'], timestamp)
        self.assertEqual(serialized['is_duplicate'], is_duplicate)
        self.assertEqual(serialized['is_refused'], is_refused)
        self.assertEqual(serialized['bgeom_type'], "Polygon")
        self.assertEqual(serialized['bgeom_srid'], sprayday.bgeom.srid)
        self.assertEqual(serialized['bgeom_coordinates'], sprayday.bgeom.tuple)
