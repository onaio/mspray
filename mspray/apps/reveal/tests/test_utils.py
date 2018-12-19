"""module to test reveal utils"""
from datetime import date

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Point
from django.test import override_settings

from mspray.apps.main.models import Household, SprayDay, SprayPoint
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reveal.utils import add_spray_data

REVEAL_SPRAY_STATUS_FIELD = "task_business_status"
REVEAL_NOT_SPRAYABLE_VALUE = "Not Sprayable"
REVEAL_SPRAYED_VALUE = "Sprayed"
REVEAL_NOT_SPRAYED_VALUE = "Not Sprayed"
REVEAL_DATE_FIELD = "task_execution_start_date"


@override_settings(
    REVEAL_SPRAY_STATUS_FIELD=REVEAL_SPRAY_STATUS_FIELD,
    REVEAL_NOT_SPRAYABLE_VALUE=REVEAL_NOT_SPRAYABLE_VALUE,
    REVEAL_SPRAYED_VALUE=REVEAL_SPRAYED_VALUE,
    REVEAL_NOT_SPRAYED_VALUE=REVEAL_NOT_SPRAYED_VALUE,
    REVEAL_DATE_FIELD=REVEAL_DATE_FIELD,
    REVEAL_GPS_FIELD="geometry",
    MSPRAY_OSM_PRESENCE_FIELD=False,
    SPRAYABLE_FIELD=REVEAL_SPRAY_STATUS_FIELD,
    MSPRAY_WAS_SPRAYED_FIELD=REVEAL_SPRAY_STATUS_FIELD,
    NOT_SPRAYABLE_VALUE=REVEAL_NOT_SPRAYABLE_VALUE,
    SPRAYED_VALUE=REVEAL_SPRAYED_VALUE,
    SPRAYED_VALUES=[REVEAL_SPRAYED_VALUE],
    MSPRAY_DATE_FIELD=REVEAL_DATE_FIELD,
    CELERY_TASK_ALWAYS_EAGER=True,
)
class TestUtils(TestBase):
    """
    Utils test class
    """

    def setUp(self):
        """
        setup test class
        """
        super().setUp()
        self._load_fixtures()

    def test_add_spray_data(self):
        """
        Test add_spray_data for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": "1337",
            "parent_id": "3537",
            "status": "Active",
            "geometry": """{
                "type": "Point",
                "coordinates": [
                    28.35517894260948,-15.41818400162254
                ]}""",
            "server_version": 1542970626309,
            "task_id": "2caa810d-d4da-4e67-838b-badb9bd86e06",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Sprayed",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "2015-09-21T1100",
            "task_server_version": 1543867945196,
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

        sprayday = SprayDay.objects.first()
        self.assertEqual(1, sprayday.submission_id)
        self.assertEqual(date(2015, 9, 21), sprayday.spray_date)
        self.assertEqual(
            Point(float(28.35517894260948), float(-15.41818400162254)).coords,
            sprayday.geom.coords,
        )
        self.assertTrue(sprayday.location is not None)
        self.assertEqual(
            sprayday.location,
            Household.objects.filter(
                geom__contains=sprayday.geom).first().location,
        )
        self.assertTrue(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertEqual(sprayday.osmid, sprayday.household.hh_id)
        self.assertTrue(sprayday.household.visited)
        self.assertTrue(sprayday.household.sprayable)
        self.assertTrue(SprayPoint.objects.filter(sprayday=sprayday).exists())

        # try again to ensure we dont create duplicate records
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

    def test_add_spray_data_polygon(self):
        """
        Test add_spray_data for reveal using polygons
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": "154147",
            "parent_id": "3951",
            "status": "Active",
            "geometry": """{
                "type":"Polygon",
                "coordinates":[
                    [
                        [28.3552415, -15.418094],
                        [28.3552963, -15.4182251],
                        [28.3552069, -15.4182598],
                        [28.3551895, -15.4182184],
                        [28.3550886, -15.4182576],
                        [28.3550511, -15.418168],
                        [28.3552415, -15.418094]
                    ]
                ]
            }""",
            "server_version": 1545204913897,
            "task_id": "d6058db2-0364-11e9-8eb2-f2801f1b9fd1",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Sprayed",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "",
            "task_server_version": 1545206825909,
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

        sprayday = SprayDay.objects.first()
        self.assertEqual(1, sprayday.submission_id)
        self.assertEqual(date(2015, 9, 21), sprayday.spray_date)
        self.assertEqual(
            Point(float(28.35517894260948), float(-15.41818400162254)).coords,
            sprayday.geom.coords,
        )
        self.assertTrue(sprayday.location is not None)
        self.assertEqual(
            sprayday.location,
            Household.objects.filter(
                geom__contains=sprayday.geom).first().location,
        )
        self.assertTrue(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertEqual(sprayday.osmid, sprayday.household.hh_id)
        self.assertTrue(sprayday.household.visited)
        self.assertTrue(sprayday.household.sprayable)
        self.assertTrue(SprayPoint.objects.filter(sprayday=sprayday).exists())

        # try again to ensure we dont create duplicate records
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

    def test_add_new_point(self):
        """
        Test adding data with new point
        """
        SprayDay.objects.all().delete()

        input_data = {
            "id": "1337",
            "parent_id": "3537",
            "status": "Active",
            "geometry": """{
                "type": "Point",
                "coordinates": [
                    28.35517894260948,-15.41818400162254
                ]}""",
            "server_version": 1542970626309,
            "task_id": "2caa810d-d4da-4e67-838b-badb9bd86e06",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Sprayed",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "2015-09-21T1100",
            "task_server_version": 1543867945196,
        }

        # we are deleting this household so that it is not found when
        # attempting to link the spray data to a structure
        Household.objects.filter(
            geom__contains=GEOSGeometry(
                input_data.get(settings.REVEAL_GPS_FIELD))
        ).first().delete()

        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

        sprayday = SprayDay.objects.first()
        self.assertEqual(1, sprayday.submission_id)
        self.assertEqual(date(2015, 9, 21), sprayday.spray_date)
        self.assertEqual(
            Point(float(28.35517894260948), float(-15.41818400162254)).coords,
            sprayday.geom.coords,
        )
        self.assertTrue(sprayday.bgeom is not None)
        self.assertTrue(sprayday.location is not None)
        self.assertEqual("Lusaka_6000", sprayday.location.name)
        self.assertTrue(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.data["osmstructure:node:id"])
        self.assertTrue(sprayday.data["newstructure/gps"])
        self.assertEqual(sprayday.osmid, -sprayday.id)
        self.assertFalse(sprayday.household)
        self.assertTrue(SprayPoint.objects.filter(sprayday=sprayday).exists())

        # try again to ensure we dont create duplicate records
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

    def test_add_new_polygon(self):
        """
        Test adding data with new Polygon
        """
        SprayDay.objects.all().delete()

        input_data = {
            "id": "154147",
            "parent_id": "3951",
            "status": "Active",
            "geometry": """{
                "type":"Polygon",
                "coordinates":[
                    [
                        [28.3520869, -15.4180991],
                        [28.3521195, -15.4180918],
                        [28.3521375, -15.4181663],
                        [28.3521081, -15.4181728],
                        [28.3521435, -15.41832],
                        [28.3520384, -15.4183435],
                        [28.3520054, -15.4182066],
                        [28.3519774, -15.4182129],
                        [28.3519579, -15.4181321],
                        [28.3519793, -15.4181273],
                        [28.3519488, -15.4180006],
                        [28.3520573, -15.4179763],
                        [28.3520869, -15.4180991]
                    ]
                ]
            }""",
            "server_version": 1545204913897,
            "task_id": "d6058db2-0364-11e9-8eb2-f2801f1b9fd1",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Sprayed",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "",
            "task_server_version": 1545206825909,
        }

        # we are deleting this household so that it is not found when
        # attempting to link the spray data to a structure
        Household.objects.filter(
            bgeom__contains=GEOSGeometry(
                input_data.get(settings.REVEAL_GPS_FIELD)
            ).centroid
        ).first().delete()

        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

        sprayday = SprayDay.objects.first()
        self.assertEqual(1, sprayday.submission_id)
        self.assertEqual(date(2015, 9, 21), sprayday.spray_date)
        self.assertEqual(
            Point(
                float(28.352047248865144), float(-15.418157849354216)).coords,
            sprayday.geom.coords,
        )
        self.assertTrue(sprayday.bgeom is not None)
        self.assertTrue(sprayday.location is not None)
        self.assertEqual("Lusaka_6000", sprayday.location.name)
        self.assertTrue(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.data["osmstructure:node:id"])
        self.assertTrue(sprayday.data["newstructure/gps"])
        self.assertEqual(sprayday.osmid, -sprayday.id)
        self.assertFalse(sprayday.household)
        self.assertTrue(SprayPoint.objects.filter(sprayday=sprayday).exists())

        # try again to ensure we dont create duplicate records
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())

    def test_add_spray_data_not_sprayed_refused(self):
        """
        Test add_spray_data REFUSED for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": "1337",
            "parent_id": "3537",
            "status": "Active",
            "geometry": """{
                "type": "Point",
                "coordinates": [
                    28.35517894260948,-15.41818400162254
                ]}""",
            "server_version": 1542970626309,
            "task_id": "2caa810d-d4da-4e67-838b-badb9bd86e06",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Not Sprayed - Refused",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "2015-09-21T1100",
            "task_server_version": 1543867945196,
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertEqual(sprayday.osmid, sprayday.household.hh_id)
        self.assertFalse(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.household.visited)
        self.assertTrue(sprayday.household.sprayable)
        self.assertTrue(SprayPoint.objects.filter(sprayday=sprayday).exists())

    def test_add_spray_data_not_sprayed(self):
        """
        Test add_spray_data NOT SPRAYED for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": "1337",
            "parent_id": "3537",
            "status": "Active",
            "geometry": """{
                "type": "Point",
                "coordinates": [
                    28.35517894260948,-15.41818400162254
                ]}""",
            "server_version": 1542970626309,
            "task_id": "2caa810d-d4da-4e67-838b-badb9bd86e06",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Not Sprayed",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "2015-09-21T1100",
            "task_server_version": 1543867945196,
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertEqual(sprayday.osmid, sprayday.household.hh_id)
        self.assertFalse(sprayday.was_sprayed)
        self.assertTrue(sprayday.sprayable)
        self.assertTrue(sprayday.household.visited)
        self.assertTrue(sprayday.household.sprayable)
        self.assertTrue(SprayPoint.objects.filter(sprayday=sprayday).exists())

    def test_add_spray_data_not_visited(self):
        """
        Test add_spray_data NOT VISITED for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": "1337",
            "parent_id": "3537",
            "status": "Active",
            "geometry": """{
                "type": "Point",
                "coordinates": [
                    28.35517894260948,-15.41818400162254
                ]}""",
            "server_version": 1542970626309,
            "task_id": "2caa810d-d4da-4e67-838b-badb9bd86e06",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Not Visited",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "2015-09-21T1100",
            "task_server_version": 1543867945196,
        }
        add_spray_data(data=input_data)
        # nothing happened
        self.assertEqual(0, SprayDay.objects.all().count())

    def test_add_spray_data_not_sprayable(self):
        """
        Test add_spray_data NOT SPRAYABLE for reveal
        """
        SprayDay.objects.all().delete()
        input_data = {
            "id": "1337",
            "parent_id": "3537",
            "status": "Active",
            "geometry": """{
                "type": "Point",
                "coordinates": [
                    28.35517894260948,-15.41818400162254
                ]}""",
            "server_version": 1542970626309,
            "task_id": "2caa810d-d4da-4e67-838b-badb9bd86e06",
            "task_spray_operator": "demoMTI",
            "task_status": "Ready",
            "task_business_status": "Not Sprayable",
            "task_execution_start_date": "2015-09-21T1000",
            "task_execution_end_date": "2015-09-21T1100",
            "task_server_version": 1543867945196,
        }
        add_spray_data(data=input_data)
        self.assertEqual(1, SprayDay.objects.all().count())
        sprayday = SprayDay.objects.first()
        self.assertFalse(sprayday.was_sprayed)
        self.assertEqual(sprayday.osmid, sprayday.household.hh_id)
        self.assertFalse(sprayday.sprayable)
        self.assertTrue(sprayday.household.visited)
        self.assertFalse(sprayday.household.sprayable)
        self.assertTrue(SprayPoint.objects.filter(sprayday=sprayday).exists())
