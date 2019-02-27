"""Module to test reactive irs utils"""
from django.test import override_settings

from mspray.apps.main.models import Household, Location
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reactive.irs.models import CommunityHealthWorker
from mspray.apps.reactive.irs.utils import get_chw_location


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

    @override_settings(
        MSPRAY_REACTIVE_IRS_CHW_CODE_PREFIX="CHW-",
        MSPRAY_REACTIVE_IRS_CHW_BUFFER=0.0005,
        MSPRAY_REACTIVE_IRS_CHW_LOCATION_LEVEL="ta",
        MSPRAY_REACTIVE_IRS_CHW_LOCATION_PARENT_LEVEL="district",
        MSPRAY_IRS_NUM_FIELD="district",
    )
    def test_get_chw_location(self):
        """Test get_chw_location"""

        some_structure = Household.objects.first()
        expected_district = Location.objects.get(
            level="district", geom__contains=some_structure.geom)

        chw = CommunityHealthWorker(
            code="97", name="Mosh", geom=some_structure.geom)
        chw.save()

        location = get_chw_location(chw=chw)

        self.assertEqual("CHW-97", location.code)
        self.assertEqual(chw.name, location.name)
        self.assertEqual(chw.bgeom, location.geom[0])
        self.assertEqual("ta", location.level)
        self.assertEqual("district", location.parent.level)
        self.assertEqual(expected_district, location.parent)
