from unittest.mock import patch

from mspray.apps.main.tests.test_base import TestBase

from mspray.apps.alerts.utils import get_district_summary_data
from mspray.apps.alerts.utils import get_district_summary_totals
from mspray.apps.alerts.utils import get_district_summary
from rest_framework.renderers import JSONRenderer


class TestUtils(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self._load_fixtures()

    def test_get_district_summary_data(self):
        """
        Test that get_district_summary_data returns exactly what we expect
        """
        expected = self._district_summary_data()
        received = get_district_summary_data()
        # to assert tha they are equal, we convert to json as comparing the
        # two ReturnList* objects doesn't work
        # * rest_framework.utils.serializer_helpers.ReturnList
        self.assertEqual(JSONRenderer().render(expected),
                         JSONRenderer().render(received))

    def test_get_district_summary_totals(self):
        """
        test that get_district_summary_totals returns exactly what we want if
        we give it a known input
        """
        district_list = self._district_summary_data()
        totals = self._district_summary_totals(district_list)
        received = get_district_summary_totals(district_list)
        self.assertEqual(totals, received)

    @patch('mspray.apps.alerts.utils.get_district_summary_data')
    @patch('mspray.apps.alerts.utils.get_district_summary_totals')
    def test_get_district_summary(self, totals_mock, summary_mock):
        """
        Test that get_district_summary calls both:
            - get_district_summary_data
            - get_district_summary_totals
        And that it returns their results as a tuple
        """
        summary_data = self._district_summary_data()
        summary_totals = self._district_summary_totals(summary_data)
        summary_mock.return_value = summary_data
        totals_mock.return_value = summary_totals
        district_list, totals = get_district_summary()
        self.assertTrue(totals_mock.called)
        self.assertTrue(summary_mock.called)
        self.assertEqual(district_list, summary_data)
        self.assertEqual(totals, summary_totals)
