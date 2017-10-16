from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.warehouse.ingest import get_druid_indexer_url


class TestIngest(TestBase):

    def setUp(self):
        TestBase.setUp(self)

    def test_get_druid_broker_url(self):
        """ test that we construct the full druid broker url successfully """
        with self.settings(DRUID_OVERLORD_URI='http://127.1.1.1',
                           DRUID_OVERLORD_PORT=8090):
            self.assertEqual(get_druid_indexer_url(),
                             'http://127.1.1.1:8090/druid/indexer/v1/task')
