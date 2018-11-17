# -*- coding: utf-8 -*-
"""MDA tests utils module."""

import codecs
import json
import os

from mspray.apps.main.utils import add_spray_data

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def get_mda_data():
    """Return MDA test submission data"""
    data = []
    path = os.path.join(FIXTURES_DIR, "mda_data.json")
    with codecs.open(path, encoding="utf-8") as spray_data_file:
        data = json.load(spray_data_file)

    return data


def load_mda_data():
    """Loads up test spray data submissions into the database."""
    data = get_mda_data()
    for row in data:
        add_spray_data(row)
