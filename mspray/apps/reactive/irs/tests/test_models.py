"""Module to test reactive irs models"""
from django.test import override_settings

from mspray.apps.main.models import Household, Location
from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.reactive.irs.models import CommunityHealthWorker


class TestModels(TestBase):
    """
    Models test class
    """

    def setUp(self):
        """
        setup test class
        """
        super().setUp()
        self._load_fixtures()

    def test_chw_model_str(self):
        """Test the str method on CommunityHealthWorker"""

        some_structure = Household.objects.first()

        chw = CommunityHealthWorker(
            name="Mosh", code="1", geom=some_structure.geom)
        chw.save()

        self.assertEqual("Mosh", chw.__str__())

    @override_settings(MSPRAY_REACTIVE_IRS_CHW_BUFFER=0.0005)
    def test_chw_model_bgeom(self):
        """Test that the bgeom is field is populated"""

        some_structure = Household.objects.first()

        chw = CommunityHealthWorker(
            name="Mosh", code="2", geom=some_structure.geom)
        chw.save()

        self.assertFalse(chw.bgeom is None)
        # TODO: we need to check the area of the bgeom

    @override_settings(
        MSPRAY_REACTIVE_IRS_CHW_CODE_PREFIX="CHW-",
        MSPRAY_REACTIVE_IRS_CHW_BUFFER=0.0005,
        MSPRAY_REACTIVE_IRS_CHW_LOCATION_LEVEL="ta",
        MSPRAY_REACTIVE_IRS_CHW_LOCATION_PARENT_LEVEL="district",
        MSPRAY_IRS_NUM_FIELD="district",
        MSPRAY_REACTIVE_IRS_CREATE_CHW_LOCATION=True,
    )
    def test_chw_link_location(self):
        """Test that the bgeom is field is populated"""

        some_structure = Household.objects.first()
        expected_district = Location.objects.get(
            level="district", geom__contains=some_structure.geom)

        chw = CommunityHealthWorker(
            name="Mosh", code="2", geom=some_structure.geom)
        chw.save()

        location = chw.location

        # pylint: disable=no-member
        self.assertEqual("CHW-2", location.code)
        self.assertEqual(chw.name, location.name)
        self.assertEqual(chw.bgeom, location.geom[0])
        self.assertEqual("ta", location.level)
        self.assertEqual("district", location.parent.level)
        self.assertEqual(expected_district, location.parent)
