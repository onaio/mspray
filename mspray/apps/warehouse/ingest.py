import json

from django.conf import settings

from mspray.apps.warehouse.utils import send_request

sprayday_datasource = getattr(settings, "DRUID_SPRAYDAY_DATASOURCE",
                              "sprayday2016")

dimensions_spec = {
    "dimensions": [
        "submission_id",
        "spray_date",
        "location_id",
        "location_name",
        "target_area_id",
        "target_area_code",
        "target_area_name",
        "rhc_id",
        "rhc_code",
        "rhc_name",
        "district_id",
        "district_code",
        "district_name",
        "sprayoperator_id",
        "sprayoperator_code",
        "sprayoperator_name",
        "team_leader_assistant_id",
        "team_leader_assistant_code",
        "team_leader_assistant_name",
        "team_leader_id",
        "team_leader_code",
        "team_leader_name",
        "sprayed",
        "sprayable",
        "submission_time",
        "reason",
        "osmid",
        "bgeom_type",
        "bgeom_srid",
        "bgeom_coordinates",
        "is_new",
        "is_refused",
        "is_duplicate",
        {
            "type": "long",
            "name": "target_area_structures"
        },
        {
            "type": "long",
            "name": "rhc_structures"
        },
        {
            "type": "long",
            "name": "district_structures"
        }
    ],
    "dimensionExclusions": [],
    "spatialDimensions": [
        {
            "dimName": "geom",
            "dims": [
                "geom_lat",
                "geom_lng"
            ]
        }
    ]
  }


def get_druid_indexer_url():
    return "{}:{}/druid/indexer/v1/task".format(settings.DRUID_OVERLORD_URI,
                                                settings.DRUID_OVERLORD_PORT)


def ingest_sprayday(file_url, intervals=None):
    """
    posts a json file on a public url to a Druid indexer task for SprayDay
    objects

    inputs:
        file_url => https://example.com/data.json
        intervals => 2013-01-01/2013-01-02
    """
    schema_file = "{}/mspray/apps/warehouse/druid-schemas/{}.json".format(
        settings.BASE_DIR, "sprayday-index-task")
    with open(schema_file) as f:
        schema = json.load(f)
    schema['spec']['dataSchema']['dataSource'] = sprayday_datasource
    schema['spec']['ioConfig']['firehose']['uris'] = [file_url]
    schema['spec']['dataSchema']['parser']['parseSpec']['dimensionsSpec'] =\
        dimensions_spec
    if intervals:
        schema['spec']['dataSchema']['granularitySpec']['intervals'] =\
            [intervals]
    schema_json = json.dumps(schema)
    return send_request(schema_json, get_druid_indexer_url())
