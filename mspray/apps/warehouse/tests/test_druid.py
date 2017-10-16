from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.warehouse.druid import get_druid_broker_url


class TestDruid(TestBase):

    def setUp(self):
        TestBase.setUp(self)

    def test_get_druid_broker_url(self):
        """ test that we construct the full druid broker url successfully """
        with self.settings(DRUID_BROKER_URI='http://127.10.10.1',
                           DRUID_BROKER_PORT=8090):
            self.assertEqual(get_druid_broker_url(), 'http://127.10.10.1:8090')
