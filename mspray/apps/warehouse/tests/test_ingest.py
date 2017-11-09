import json

from unittest.mock import patch

from django.conf import settings

from mspray.apps.main.tests.test_base import TestBase
from mspray.apps.warehouse.ingest import get_druid_indexer_url, ingest_sprayday
from mspray.apps.warehouse.ingest import dimensions_spec, sprayday_datasource
from mspray.apps.warehouse.ingest import get_sprayday_schema


class TestIngest(TestBase):

    def setUp(self):
        TestBase.setUp(self)

    def test_get_druid_broker_url(self):
        """ test that we construct the full druid indexer url successfully """
        with self.settings(DRUID_OVERLORD_URI='http://127.1.1.1',
                           DRUID_OVERLORD_PORT=8090):
            self.assertEqual(get_druid_indexer_url(),
                             'http://127.1.1.1:8090/druid/indexer/v1/task')

    def test_get_sprayday_schema(self):
        """
        Test that get_sprayday_schema returns what we expect
        """
        schema_file = "{}/mspray/apps/warehouse/druid-schemas/{}.json".format(
            settings.BASE_DIR, "sprayday-index-task")
        with open(schema_file) as f:
            expected = json.load(f)
        schema = get_sprayday_schema()
        self.assertEqual(expected, schema)

    @patch('mspray.apps.warehouse.ingest.send_request')
    def test_ingest_sprayday(self, mock):
        """
        Test that ingest_sprayday actually sends the expected payload to Druid
        """
        file_url = "https://example.com/data.json"
        intervals = "2013-01-01/2013-01-02"

        schema = get_sprayday_schema()
        schema['spec']['dataSchema']['dataSource'] = sprayday_datasource
        schema['spec']['ioConfig']['firehose']['uris'] = [file_url]
        schema['spec']['dataSchema']['parser']['parseSpec']['dimensionsSpec']\
            = dimensions_spec
        schema['spec']['dataSchema']['granularitySpec']['intervals'] =\
            [intervals]
        schema_json = json.dumps(schema)

        ingest_sprayday(file_url, intervals)

        self.assertTrue(mock.called)
        args, kwargs = mock.call_args_list[0]
        self.assertEqual(args[0], schema_json)
        self.assertEqual(args[1], get_druid_indexer_url())
