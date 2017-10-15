import json

from django.conf import settings

from mspray.apps.warehouse.utils import send_request

household_datasource = getattr(settings, "DRUID_HOUSEHOLD_DATASOURCE",
                               "household2016")
sprayday_datasource = getattr(settings, "DRUID_SPRAYDAY_DATASOURCE",
                              "sprayday2016")


def ingest_household(path):
    schema = "{}//mspray/apps/warehouse/druid-schemas/household.json".format(
        settings.BASE_DIR)
    with open(schema) as f:
        schema_dict = json.load(f)
    schema_dict['spec']['dataSchema']['dataSource'] = household_datasource
    schema_dict['spec']['ioConfig']['inputSpec']['paths'] = path
    schema_json = json.dumps(schema_dict)
    return send_request(schema_json, '{}/druid/indexer/v1/task'.format(
            settings.DRUID_OVERLORD_URI))


def ingest_sprayday(path):
    schema = "{}//mspray/apps/warehouse/druid-schemas/sprayday.json".format(
        settings.BASE_DIR)
    with open(schema) as f:
        schema_dict = json.load(f)
    schema_dict['spec']['dataSchema']['dataSource'] = sprayday_datasource
    schema_dict['spec']['ioConfig']['inputSpec']['paths'] = path
    schema_json = json.dumps(schema_dict)
    return send_request(schema_json, '{}/druid/indexer/v1/task'.format(
            settings.DRUID_OVERLORD_URI))
