# -*- coding: utf-8 -*-
"""Definitions variables used by the definitions-and-conditions.html template.

Needs to be imported and relevant key updated into the view context variables.
"""
# pylint: disable=line-too-long
DEFINITIONS = {
    "mopup": {
        "colors": {
            "title": "Structures remaining to spray to reach 90% Spray Effectiveness:",  # noqa
            "colors": [
                ("Green", ">", "10"),
                ("Orange", ">=10", "<20"),
                ("Red", ">=20", ""),
            ],
        }
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
    "performance:district": {
        "definitions": [
            "a - Start time is determined from the time the first form is completed per day per operator",  # noqa
            "b - Finish time is determined from the time the last form is started per day per operator",  # noqa
        ],
        "performance_conditions": True,
    },
    "tla": {
        "definitions": [
            "a - Start time is determined from the time the first form is completed per day per operator",  # noqa
            "b - Finish time is determined from the time the last form is started per day per operator",  # noqa
        ],
        "performance_conditions": True,
    },
    "sop": {
        "definitions": [
            "Found Difference TODAY is SOP Summary found minus HH Submissions found.",  # noqa
            "Sprayed Difference TODAY should just be for today i.e. the last row in the daily spray operator table.",  # noqa
            "a - Start time is determined from the time the first form is completed per day per operator",  # noqa
            "b - Finish time is determined from the time the last form is started per day per operator",  # noqa
        ],
        "performance_conditions": True,
    },
}
