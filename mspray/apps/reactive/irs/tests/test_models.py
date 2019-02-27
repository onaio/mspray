"""Module to test reacctivre irs models"""
from django.test import override_settings

from mspray.apps.main.models import Household
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
            name="Mosh",
            geom=some_structure.geom,
            location=some_structure.location)
        chw.save()

        self.assertEqual("Mosh", chw.__str__())

    @override_settings(MSPRAY_REACTIVE_IRS_CHW_BUFFER=0.0005)
    def test_chw_model_bgeom(self):
        """Test that the bgeom is field is populated"""

        some_structure = Household.objects.first()

        chw = CommunityHealthWorker(
            name="Mosh",
            geom=some_structure.geom,
            location=some_structure.location)
        chw.save()

        self.assertFalse(chw.bgeom is None)
        # TODO: we need to check the area of the bgeom
