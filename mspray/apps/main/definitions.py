# -*- coding: utf-8 -*-
"""Definitions variables used by the definitions-and-conditions.html template.

Needs to be imported and relevant key updated into the view context variables.
"""
# pylint: disable=line-too-long
START_TIME = "a - Start time is determined from the time the first form is completed per day per operator"  # noqa
FINISH_TIME = "b - Finish time is determined from the time the last form is started per day per operator"  # noqa

DEFINITIONS = {
    "mopup": {
        "IRS": {
            "colors": {
                "title": "Structures remaining to spray to reach 90% Spray Effectiveness:",  # noqa
                "colors": [
                    ("Green", ">", "10"),
                    ("Orange", ">=10", "<20"),
                    ("Red", ">=20", ""),
                ],
            },
            "spray_area_label": "Spray Area",
            "visited_sprayed_label": "Visited Sprayed",
            "structures_remaining_label": "Structures remaining to spray to reach 90% SE",  # noqa
            "spray_effectiveness_label": "Spray Effectiveness",
            "spray_coverage_label": "Spray Coverage",
            "spray_areas_to_mopup_label": "# Spray Areas to Mop-up",
            "structures_to_mopup_90_label": "Structures to spray for areas to reach 90%*",  # noqa
        },
        "MDA": {
            "colors": {
                "title": "Structures remaining to receive treatment to reach 90% Received Success Rate:",  # noqa
                "colors": [
                    ("Green", ">", "10"),
                    ("Orange", ">=10", "<20"),
                    ("Red", ">=20", ""),
                ],
            },
            "spray_area_label": "Eligible Area",
            "visited_sprayed_label": "Structures Received",
            "structures_remaining_label": "Structures remaining to receive treatment to reach 90% SE",  # noqa
            "spray_effectiveness_label": "Structures Received Success Rate",
            "spray_coverage_label": "Structures Received Coverage",
            "spray_areas_to_mopup_label": "# Eligible Areas to Mop-up",
            "structures_to_mopup_90_label": "Structures to reach for areas to reach 90%*",  # noqa
        },
    },
    "district": {
        "definitions": [
            "a - A spray area is defined as 'Visited' if at least 20% of"
            " the structures on the ground within that area have been found and have data recorded against them.",  # noqa
            "b - A spray area is defined as 'Sprayed Effectively' if at least 90% of the structures on the ground within that area have been sprayed.",  # noqa
        ],
        "colors": {
            "title": "1. Health Facility shapefiles will appear colored based on Spray Effectiveness as below:",  # noqa
            "colors": [
                ("Green", ">=", "90%"),
                ("Orange", "90%", "75%"),
                ("Red", "75%", "20%"),
                ("Yellow", "<", "20%"),
            ],
        },
    },
    "RHC": {
        "definitions": [
            "a - A spray area is defined as 'Visited' if at least 20% of the structures within that area have been found and have data recorded against them.",  # noqa
            "b - A spray area is defined as 'Sprayed Effectively' if at least 90% of the structures within that area have been sprayed.",  # noqa
        ],
        "colors": {
            "title": "1. Spray Area shapefiles will appear colored based on Spray Effectiveness as below:",  # noqa
            "colors": [
                ("Green", ">=", "90%"),
                ("Orange", "90%", "75%"),
                ("Red", "75%", "20%"),
                ("Yellow", "<", "20%"),
            ],
        },
    },
    "ta": {
        "definitions": [
            "Spray Effectiveness: Structures sprayed / structures on the ground",  # noqa
            "Found Coverage: Structures found / structures on the ground",
            "Spray Coverage:	Structures sprayed / structures found",
        ],
        "colors": {
            "title": "Spray Effectiveness colors:",
            "colors": [
                ("Green", ">=", "90%"),
                ("Orange", "90%", "75%"),
                ("Red", "75%", "20%"),
                ("Yellow", "<", "20%"),
            ],
        },
    },
    "irs": {
        "definitions": [
            "Spray Coverage: Structures sprayed / structures on the ground",  # noqa
            "Found Coverage: Structures found / structures on the ground",
            "Spray Success Rate: Structures sprayed / structures found",
        ],
        "colors": {
            "title":
            "Spray Coverage colors:",
            "colors": [
                ("Green", ">=", "90%"),
                ("Orange", "90%", "75%"),
                ("Red", "75%", "20%"),
                ("Yellow", "<", "20%"),
            ],
        },
    },
    "performance:district": {
        "definitions": [START_TIME, FINISH_TIME],
        "performance_conditions": True,
    },
    "tla": {
        "definitions": [START_TIME, FINISH_TIME],
        "performance_conditions": True,
        "show_data_quality_definitions": False,
    },
    "sop": {
        "definitions": [
            "Found Difference TODAY is SOP Summary found minus HH Submissions found.",  # noqa
            "Sprayed Difference TODAY should just be for today i.e. the last row in the daily spray operator table.",  # noqa
            START_TIME,
            FINISH_TIME,
        ],
        "performance_text": "Average structures sprayed per day per SO",
        "performance_conditions": True,
        "show_data_quality_definitions": False,
    },
    "mda-sop": {
        "definitions": [START_TIME, FINISH_TIME],
        "performance_text": "Average residential structures per day per SO",
        "performance_conditions": True,
        "show_data_quality_definitions": False,
    },
    "mda-sop-daily": {
        "definitions": [START_TIME, FINISH_TIME],
        "performance_conditions": False,
    },
}
