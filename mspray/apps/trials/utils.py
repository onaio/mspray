# -*- coding: utf-8 -*-
"""Trials util module"""

from django.conf import settings
from django.db.utils import IntegrityError

from mspray.apps.main.models import Household, Location
from mspray.apps.trials.models import Sample
from mspray.libs.ona import fetch_form_data, fetch_osm_xml
from mspray.libs.osm import parse_osm_nodes, parse_osm_ways


def download_osm_geom(data, osm_field):
    """Downloads the OSM data from Ona and creates a geom object.
    """
    filename = data.get(osm_field)
    osm_xml = fetch_osm_xml(data, filename)
    if osm_xml is not None:
        geoms = parse_osm_ways(osm_xml) or parse_osm_nodes(osm_xml)

        if geoms:
            return geoms[0]['geom']

    return None


def get_sample_geom(spray_area, household_id, form_id):
    """Downloads OSM information for a household from the collections form.
    """
    osm_field = 'osmstructure'
    query = {'spray_area': spray_area, 'HHID': household_id}
    form_data = fetch_form_data(form_id, query=query)
    for row in form_data:
        osmid = row.get('%s:way:id' % osm_field)
        if osmid:
            try:
                household = Household.objects.get(hh_id=osmid)
            except Household.DoesNotExist:
                pass
            else:
                return household.bgeom

            # We already have a sample with the geom
            sample = Sample.objects.filter(
                spray_area__name=spray_area,
                household_id=household_id,
                geom__isnull=False).first()
            if sample:
                return sample.geom

        # download OSM file
        geom = download_osm_geom(row, osm_field)
        if geom:
            return geom

    return None


def load_samples_from_ona(form_id=None, collections_form_id=None):
    """Loads the Ento Counts form into the Sample model."""
    if not form_id:
        form_id = getattr(settings, 'SAMPLE_FORM_ID', None)
    if not form_id:
        return None
    if not collections_form_id:
        collections_form_id = getattr(settings, 'COLLECTIONS_FORM_ID', None)

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
            sample = Sample.objects.create(
                collection_method=row['collection_method'],
                district=district,
                household_id=row['HHID'],
                sample_date=row['date'],
                spray_area=spray_area,
                submission_id=submission_id,
                visit=row['visit'],
                data=row)
        except IntegrityError:
            sample = Sample.objects.get(submission_id=submission_id)
            if not sample.geom:
                set_sample_geom(sample, collections_form_id)
            continue
        else:
            set_sample_geom(sample, collections_form_id)


def set_sample_geom(sample, collections_form_id):
    """Downloads the household geom and saves it with the sample.
    """
    if not collections_form_id:
        return

    geom = get_sample_geom(sample.spray_area.name, sample.household_id,
                           collections_form_id)
    if geom:
        sample.geom = geom
        sample.save()
