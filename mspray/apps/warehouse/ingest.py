import os
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
    return "{uri}:{port}/druid/indexer/v1/task".format(
                uri=settings.DRUID_OVERLORD_URI,
                port=settings.DRUID_OVERLORD_PORT)


def get_sprayday_schema():
    schema_file = os.path.join(
        settings.BASE_DIR,
        "mspray/apps/warehouse/druid-schemas/sprayday-index-task.json")
    with open(schema_file) as f:
        schema = json.load(f)
    return schema


def get_sprayday_hadoop_schema():
    schema_file = os.path.join(
        settings.BASE_DIR,
        "mspray/apps/warehouse/druid-schemas/sprayday-hadoop.json")
    with open(schema_file) as f:
        schema = json.load(f)
    return schema


def ingest_sprayday(file_url, intervals=None,
                    timestamp_column=settings.DRUID_TIMESTAMP_COLUMN):
    """
    posts a json file on a public url to a Druid indexer task for SprayDay
    objects

    inputs:
        file_url => https://example.com/data.json
        intervals => 2013-01-01/2013-01-02

    """
    if settings.DRUID_USE_INDEX_HADOOP:
        schema = get_sprayday_hadoop_schema()
        schema['spec']['ioConfig']['inputSpec']['paths'] = file_url
    else:
        schema = get_sprayday_schema()
        schema['spec']['ioConfig']['firehose']['uris'] = [file_url]

    schema['spec']['dataSchema']['dataSource'] = sprayday_datasource
    parse_spec = schema['spec']['dataSchema']['parser']['parseSpec']
    parse_spec['dimensionsSpec'] = dimensions_spec
    parse_spec['timestampSpec']['column'] = timestamp_column
    if intervals:
        schema['spec']['dataSchema']['granularitySpec']['intervals'] =\
            [intervals]

    schema_json = json.dumps(schema)
    return send_request(schema_json, get_druid_indexer_url())
