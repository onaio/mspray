from unittest.mock import patch

from django.conf import settings

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.alerts.emails import send_weekly_update_email


class TestEmails(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self._load_fixtures()

    @patch('mspray.apps.alerts.emails.get_contacts')
    @patch('mspray.apps.alerts.emails.get_district_summary')
    @patch('mspray.apps.alerts.emails.weekly_update_email')
    def test_send_weekly_update_email(self, email_mock, summary_mock,
                                      contacts_mock):
        """
        Test that send_weekly_update_email works as expected by verifying that
        it calls:
            - get_contacts with the correct arguments
            - get_district_summary
            - weekly_update_email with the correct arguments
        """
        self._load_fixtures()
        rapidpro_contact = self._get_rapidpro_contact()
        district_list = self._district_summary_data()
        totals = self._district_summary_totals(district_list)
        contacts_mock.return_value = [rapidpro_contact]
        summary_mock.return_value = district_list, totals
        send_weekly_update_email()
        self.assertTrue(contacts_mock.called)
        self.assertTrue(summary_mock.called)
        self.assertTrue(email_mock.called)
        contact_args, contact_kwargs = contacts_mock.call_args_list[0]
        self.assertEqual(contact_args[0],
                         settings.RAPIDPRO_WEEKLY_UPDATE_CONTACT_GROUP)
        email_args, email_kwargs = email_mock.call_args_list[0]
        self.assertEqual(email_args[0], 'Mosh <one@example.com>')
        self.assertEqual(email_args[1], district_list)
        self.assertEqual(email_args[2], totals)
