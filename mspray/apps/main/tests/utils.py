# -*- coding: utf-8 -*-
"""
Reusable test util constants and functions.
"""
import os

from django.core.management import call_command

SENSITIZATION_VISIT_DATA = {
    "osmstructure:way:id": "528511960",
    "osmstructure:sensitized": "Yes",
    "values_from_omk/sensitized": "Yes",
    "date": "2018-09-25",
    "coordinator_name": "1",
    "tla_name": "1",
    "spray_area": "01_1",
    "end": "2018-09-25T13:06:05.254+02",
    "district": "1",
    "osmstructure:ctr:lat": -15.418780034209806,
    "health_facility": "1",
    "start": "2018-09-25T13:04:04.015+02",
    "sensitized1/Villagename": "Kabulonga",
    "osmstructure": "f46fedfe58eb4aa451e6404a485ee5755fb37a41.osm",
    "today": "2018-09-25",
    "meta/instanceID": "uuid:02d92c3a-83a1-49a3-8a67-a2a22b54833a",
    "_uuid": "02d92c3a-83a1-49a3-8a67-a2a22b54833a",
    "meta/instanceName": "2018-09-25 - SEN - 1 -Yes -Kabulonga",
    "imei": "357770076803649",
    "osmstructure:ctr:lon": 28.35196267147328,
    "sensitized1/hh_pop": 10,
    "_xform_id": 343725,
    "_submission_time": "2018-09-25T11:06:15",
    "_attachments": [
        {
            "mimetype": "text/xml",
            "name": "f46fedfe58eb4aa451e6404a485ee5755fb37a41.osm",
            "download_url": (
                "/api/v1/files/9440768?filename="
                "akros_health/attachments/343725_VL_SEN_2018/"
                "f46fedfe58eb4aa451e6404a485ee5755fb37a41.osm"
            ),
            "filename": (
                "akros_health/attachments/343725_VL_SEN_2018/"
                "f46fedfe58eb4aa451e6404a485ee5755fb37a41.osm"
            ),
            "instance": 34857737,
            "id": 9440768,
            "xform": 343725,
        }
    ],
    "deviceid": "357770076803649",
    "osmstructure:building": "yes",
    "_id": 34857737,
    "subscriberid": "645017733573627",
}

MOBILISATION_VISIT_DATA = {
    "osmstructure:way:id": "528511960",
    "osmstructure:mobilised": "Yes",
    "values_from_omk/mobilised": "Yes",
    "date": "2018-09-25",
    "coordinator_name": "1",
    "tla_name": "1",
    "spray_area": "01_1",
    "end": "2018-09-25T13:06:05.254+02",
    "district": "1",
    "osmstructure:ctr:lat": -15.418780034209806,
    "health_facility": "1",
    "start": "2018-09-25T13:04:04.015+02",
    "sensitized1/Villagename": "Kabulonga",
    "osmstructure": "f46fedfe58eb4aa451e6404a485ee5755fb37a41.osm",
    "today": "2018-09-25",
    "meta/instanceID": "uuid:02d92c3a-83a1-49a3-8a67-a2a22b54833a",
    "_uuid": "02d92c3a-83a1-49a3-8a67-a2a22b54833a",
    "meta/instanceName": "2018-09-25 - SEN - 1 -Yes -Kabulonga",
    "imei": "357770076803649",
    "osmstructure:ctr:lon": 28.35196267147328,
    "sensitized1/hh_pop": 10,
    "_xform_id": 343725,
    "_submission_time": "2018-09-25T11:06:15",
    "_attachments": [
        {
            "mimetype": "text/xml",
            "name": "f46fedfe58eb4aa451e6404a485ee5755fb37a41.osm",
            "download_url": (
                "/api/v1/files/9440768?filename="
                "akros_health/attachments/343725_VL_SEN_2018/"
                "f46fedfe58eb4aa451e6404a485ee5755fb37a41.osm"
            ),
            "filename": (
                "akros_health/attachments/343725_VL_SEN_2018/"
                "f46fedfe58eb4aa451e6404a485ee5755fb37a41.osm"
            ),
            "instance": 34857737,
            "id": 9440768,
            "xform": 343725,
        }
    ],
    "deviceid": "357770076803649",
    "osmstructure:building": "yes",
    "_id": 34857737,
    "subscriberid": "645017733573627",
}


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_district_shapefile():
    """
    Loads district test shapefiles.
    """
    path = os.path.join(FIXTURES_DIR, "Lusaka", "districts")
    call_command(
        "load_location_shape_file", path, "NAME", "district", skip_parent="yes"
    )


def load_health_facility_shapefile():
    """
    Loads health facility test shapefiles.
    """
    path = os.path.join(FIXTURES_DIR, "Lusaka", "HF")
    call_command(
        "load_location_shape_file",
        path,
        "HFC_NAME",
        "RHC",
        parent_field="DISTRICT",
        parent_level="district",
    )


def load_spray_area_shapefile():
    """
    Loads spray_area test shapefiles.
    """
    path = os.path.join(FIXTURES_DIR, "Lusaka", "SA")
    call_command(
        "load_location_shape_file",
        path,
        "SPRAYAREA",
        "ta",
        parent_field="HFC_NAME",
        parent_level="RHC",
    )


def load_osm_structures():
    """
    Loads test OSM files.
    """
    path = os.path.join(FIXTURES_DIR, "Lusaka", "OSM")
    call_command("load_osm_hh", path)


def data_setup():
    """Loads up initial test fixtures into the database."""
    load_district_shapefile()
    load_health_facility_shapefile()
    load_spray_area_shapefile()
    load_osm_structures()
