# -*- coding: utf-8 -*-
"""Trials util module"""

from django.conf import settings
from django.db.utils import IntegrityError

from mspray.apps.main.models import Location
from mspray.apps.trials.models import Sample
from mspray.libs.ona import fetch_form_data


def load_samples_from_ona(form_id=None):
    """Loads the Ento Counts form into the Sample model."""
    if not form_id:
        form_id = getattr(settings, 'SAMPLE_FORM_ID', None)
    if not form_id:
        return None

    data = fetch_form_data(form_id) or []

    for row in data:
        submission_id = row['_id']
        district = Location.objects.filter(level='district').get(
            code=int(row['district']))
        try:
            spray_area = Location.objects.filter(
                level='ta',
                parent__parent=district).get(name=row['spray_area'])
        except Location.DoesNotExist:
            print("Skipping:", row['spray_area'])
            continue

        row['fem_anoph'] = int(row['fem_anoph'])
        row['bl_anoph'] = int(row['bl_anoph'])
        row['grav_anoph'] = int(row['grav_anoph'])
        row['male_anoph'] = int(row['male_anoph'])
        row['tot_anoph'] = int(row['tot_anoph'])
        row['fem_culex'] = int(row['fem_culex'])
        row['male_culex'] = int(row['male_culex'])
        row['tot_culex'] = int(row['tot_culex'])
        row['fem_aedes'] = int(row['fem_aedes'])
        row['male_aedes'] = int(row['male_aedes'])
        row['tot_aedes'] = int(row['tot_aedes'])
        row['tot_mosq'] = int(row['tot_mosq'])

        if 'visit' in row:
            try:
                row['visit'] = int(row['visit'])
            except ValueError:
                if row['visit'] == 'n/a':
                    row['visit'] = 1
        else:
            row['visit'] = 1

        try:
            Sample.objects.create(
                collection_method=row['collection_method'],
                district=district,
                household_id=row['HHID'],
                sample_date=row['date'],
                spray_area=spray_area,
                submission_id=submission_id,
                visit=row['visit'],
                data=row)
        except IntegrityError:
            continue
