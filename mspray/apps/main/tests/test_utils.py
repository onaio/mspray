from unittest.mock import patch

from django.conf import settings
from django.db.models import Count

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.main.models import SprayDay, TeamLeader, TeamLeaderAssistant
from mspray.apps.main.models import SprayOperator, SprayOperatorDailySummary
from mspray.apps.main.models import Household
from mspray.apps.main.models.spray_day import DATA_ID_FIELD
from mspray.apps.main.utils import add_spray_data
from mspray.apps.main.utils import avg_time_tuple
from mspray.apps.main.utils import avg_time_per_group
from mspray.apps.main.utils import get_formid
from mspray.apps.main.utils import link_sprayday_to_actors
from mspray.apps.main.utils import remove_duplicate_sprayoperatordailysummary
from mspray.apps.main.utils import add_spray_operator_daily
from mspray.apps.main.utils import remove_household_geom_duplicates
from mspray.celery import app

SUBMISSION_DATA = [{
    "osm_building": "OSMWay-1760.osm",
    "today": "2015-09-21",
    "_id": 3563261,
    "_attachments": [{
        "mimetype": "text/xml",
        "download_url": "/api/v1/files/583377?filename=osm_experiments/attachments/OSMWay-1942.osm",  # noqa
        "filename": "osm_experiments/attachments/OSMWay-1942.osm",
        "instance": 3542171,
        "id": 583377,
        "xform": 79639
    }],
    "meta/instanceID": "uuid:da51a5c9-e87d-49df-9559-43f670f2079b"
}]


class TestUtils(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        app.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_avg_time_tuple(self):
        times = [(15, 21), (15, 11), (8, 47)]
        self.assertEqual(avg_time_tuple(times), (13, 6))
        times = [(23, 57), (3, 24), (2, 39)]
        self.assertEqual(avg_time_tuple(times), (10, 0))
        times = [(15, 18), (18, 35), (11, 26)]
        self.assertEqual(avg_time_tuple(times), (15, 6))

    def test_avg_time_per_so(self):
        results = [
            ('SOP0483', '2015-09-01', 12.0, 59.0),
            ('SOP0483', '2015-09-02', 15.0, 34.0),
            ('SOP0483', '2015-09-03', 11.0, 57.0),
            ('SOP0484', '2015-09-01', 13.0, 57.0),
            ('SOP0484', '2015-09-02', 15.0, 46.0),
            ('SOP0484', '2015-09-03', 14.0, 15.0),
            ('SOP0485', '2015-09-01', 12.0, 30.0),
            ('SOP0485', '2015-09-02', 15.0, 51.0),
            ('SOP0485', '2015-09-03', 12.0, 20.0)
        ]

        self.assertEqual(avg_time_per_group(results), (13, 54))
        self.assertEqual(avg_time_per_group([]), (None, None))

    @patch('mspray.apps.main.utils.link_sprayday_to_actors')
    def test_add_spray_data(self, mock):
        """
        test that add spray daya works as expected
        """
        count = SprayDay.objects.count()
        add_spray_data(SUBMISSION_DATA[0])
        self.assertTrue(SprayDay.objects.count() > count)
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(kwargs['sprayday'], SprayDay.objects.first())
        self.assertEqual(kwargs['data'], SUBMISSION_DATA[0])

    @patch('mspray.apps.main.tasks.fetch_osm_xml')
    @patch('mspray.apps.main.utils.run_tasks_after_spray_data')
    def test_add_spray_data_with_osm(self, mock, mock2):
        """
        Test that add_spray_data createsa SprayDay object and that if it has
        OSM data it runs run_tasks_after_spray_data
        """
        self._load_fixtures()
        # get submission data that has OSM info
        sp = SprayDay.objects.filter(
                data__has_key=settings.MSPRAY_OSM_PRESENCE_FIELD).first()
        data = sp.data
        # change the _id field so that we can reuse this data
        data[DATA_ID_FIELD] = 111
        count = SprayDay.objects.count()
        sp = add_spray_data(data)
        self.assertTrue(SprayDay.objects.count() > count)
        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0], sp)

    def test_link_sprayday_to_actors(self):
        """
        Test that from link_sprayday_to_actors correctly links a sprayday
        object with the right spray operator, team leader assistant and team
        leader.
        """
        self._load_fixtures()
        so = SprayOperator.objects.first()
        tl = TeamLeader.objects.first()
        tla = TeamLeaderAssistant.objects.first()
        sprayday = SprayDay.objects.first()
        data = {
            settings.MSPRAY_SPRAY_OPERATOR_CODE: so.code,
            settings.MSPRAY_TEAM_LEADER_CODE: tl.code,
            settings.MSPRAY_TEAM_LEADER_ASSISTANT_CODE: tla.code
        }
        # make sure we have the objects to work with
        self.assertFalse(None in [so, tl, tla, sprayday])

        # set fields to None so that we can test with certainty that the right
        # ones were added
        sprayday.spray_operator = None
        sprayday.team_leader_assistant = None
        sprayday.team_leader = None
        sprayday.save()

        link_sprayday_to_actors(sprayday, data)

        sprayday.refresh_from_db()
        self.assertEqual(sprayday.spray_operator, so)
        self.assertEqual(sprayday.team_leader_assistant, tla)
        self.assertEqual(sprayday.team_leader, tl)
        self.assertEqual(sprayday.data['sprayformid'],
                         get_formid(so, sprayday.spray_date))

    def test_remove_duplicate_sprayoperatordailysummary(self):
        """
        test that remove_duplicate_sprayoperatordailysummary:
            removes all duplicates
            does not delete everything
            retains the desired objects
        """
        self._load_fixtures()
        dups = (
            SprayOperatorDailySummary.objects.values('spray_form_id')
                                             .annotate(count=Count('id'))
                                             .values('spray_form_id')
                                             .order_by()
                                             .filter(count__gt=1)
        )
        # get objects that need to be kept and objects that need to be removed
        to_keep = []
        to_remove = []
        for dup in dups:
            objects = SprayOperatorDailySummary.objects.filter(
                        spray_form_id=dup['spray_form_id']).order_by(
                            '-submission_id')
            # keep this
            to_keep.append(objects.first().id)
            # remove these
            to_remove = to_remove + [x.id for x in objects.exclude(
                                                        id=objects.first().id)]

        # import ipdb; ipdb.set_trace()
        remove_duplicate_sprayoperatordailysummary()
        # check that we removed what we needed to remove and kept what we
        # needed to keep
        self.assertEqual(len(to_keep),
                         SprayOperatorDailySummary.objects.filter(
                            id__in=to_keep).count())
        self.assertEqual(SprayOperatorDailySummary.objects.filter(
                            id__in=to_remove).count(), 0)
        # check that no duplicates exist
        dups2 = (
            SprayOperatorDailySummary.objects.values('spray_form_id')
                                             .annotate(count=Count('id'))
                                             .values('spray_form_id')
                                             .order_by()
                                             .filter(count__gt=1)
        )
        self.assertEqual(dups2.count(), 0)

    @patch('mspray.apps.main.utils.calculate_data_quality_check')
    def test_add_spray_operator_daily(self, mock):
        """
        Test that add_spray_operator_daily actually adds a new
        SprayOperatorDailySummary object
        """
        self._load_fixtures()
        data = SprayOperatorDailySummary.objects.first().data
        SprayOperatorDailySummary.objects.all().delete()
        self.assertEqual(SprayOperatorDailySummary.objects.count(), 0)
        add_spray_operator_daily(data)
        self.assertTrue(mock.called)
        self.assertEqual(SprayOperatorDailySummary.objects.count(), 1)

    @patch('mspray.apps.main.utils.calculate_data_quality_check')
    def test_update_spray_operator_daily(self, mock):
        """
        Test that add_spray_operator_daily actually updates an existing record
        if it receives data for the same spray_operator in the same date
        """
        self._load_fixtures()
        data = SprayOperatorDailySummary.objects.first().data
        SprayOperatorDailySummary.objects.all().delete()
        self.assertEqual(SprayOperatorDailySummary.objects.count(), 0)
        add_spray_operator_daily(data)
        self.assertTrue(mock.called)
        self.assertEqual(SprayOperatorDailySummary.objects.count(), 1)
        new_data = data.copy()
        new_data['supervisor_name'] = "MOSH"
        new_data['sprayed'] = 97
        new_data['found'] = 100
        add_spray_operator_daily(new_data)
        self.assertEqual(SprayOperatorDailySummary.objects.count(), 1)
        obj = SprayOperatorDailySummary.objects.first()
        self.assertEqual(obj.sprayed, new_data['sprayed'])
        self.assertEqual(obj.found, new_data['found'])
        self.assertEqual(obj.data.get('supervisor_name'), "MOSH")
        self.assertEqual(mock.call_count, 2)

    def test_remove_household_geom_duplicates(self):
        """
        Test that remove_household_geom_duplicates removes duplicate Household
        objects
        """
        self._load_fixtures()
        hh_obj = Household.objects.first()
        # create a duplicate Household object
        duplicate_hh_obj = Household(
            hh_id=-99999999,
            geom=hh_obj.geom,
            bgeom=hh_obj.bgeom,
            location=hh_obj.location,
            data=hh_obj.data
        )
        duplicate_hh_obj.save()
        # check that we actually have duplicates
        self.assertEqual(Household.objects.filter(geom=hh_obj.geom).count(), 2)
        # remove the duplicate and test that it is removed
        remove_household_geom_duplicates(hh_obj.location)
        self.assertEqual(Household.objects.filter(geom=hh_obj.geom).count(), 1)
