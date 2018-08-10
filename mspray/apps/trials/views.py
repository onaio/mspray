# -*- coding: utf-8 -*-
"""Trials views"""
from collections import OrderedDict

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, render

from mspray.apps.main.models import Location
from mspray.apps.trials.models import Sample


def get_samples_for_method(queryset, collection_method, key, key_name):
    """Return the queryset with the sam of tot_mosq for a given
    collection_method.
    """
    params = {
        key: Sum(
            Cast(KeyTextTransform('tot_mosq', 'data'), models.IntegerField()))
    }
    return queryset.filter(collection_method=collection_method)\
        .values(key_name).distinct().order_by(key_name)\
        .annotate(**params)


def _merge_results_by_district(results, iter_data, key, key_name):
    """Return merges data represented by key in iter_data to the results
    dictionary.
    """
    for row in iter_data:
        try:
            results[row[key_name]].update({key: row[key]})
        except KeyError:
            results[row[key_name]] = {key: row[key]}

    return results


def index(request):
    """Index view"""
    surveys = Sample.objects.values_list(
        'visit', flat=True).order_by('visit').distinct()
    results = {}
    for survey in surveys:
        queryset = Sample.objects.filter(visit=survey)
        hh_per_district = queryset.values('district__name', 'district_id')\
            .distinct()\
            .annotate(houses_reached=Count('household_id', distinct=True))\
            .order_by('district__name')
        row = OrderedDict(
            sorted(
                {
                    rec['district__name']: {
                        'houses_reached': rec['houses_reached'],
                        'location_id':  rec['district_id'],
                    }
                    for rec in hh_per_district
                }.items(),
                key=lambda t: t[0]))
        prokopacks = get_samples_for_method(queryset, Sample.PROKOPACK,
                                            'prokopack', 'district__name')
        row = _merge_results_by_district(row, prokopacks, 'prokopack',
                                         'district__name')
        light_traps = get_samples_for_method(queryset, Sample.CDC_LIGHT_TRAP,
                                             'light_trap', 'district__name')
        row = _merge_results_by_district(row, light_traps, 'light_trap',
                                         'district__name')

        results[survey] = {
            'rows': row,
            'totals': [
                hh_per_district.aggregate(
                    total_houses_reached=Sum('houses_reached')),
                prokopacks.aggregate(total_prokopacks=Sum('prokopack')),
                light_traps.aggregate(total_light_traps=Sum('light_trap')),
            ]
        }  # yapf: disable

    response = {}
    for i, j in results.items():
        for a, b in j['rows'].items():  # pylint: disable=invalid-name
            try:
                response[a].update({i: b})
            except KeyError:
                response[a] = {i: b}
            response[a][i].update({'totals': j['totals']})

    response = OrderedDict(sorted(response.items(), key=lambda t: t[0]))

    return render(request, 'trials/index.html', {
        'results': response,
        'surveys': surveys,
        'trials': True,
        'level': 'District',
        'title': 'Province: Eastern',
    })


def site(request, site_id):
    """Spray Areas in a district trials view.
    """
    surveys = Sample.objects.values_list(
        'visit', flat=True).order_by('visit').distinct()

    location = get_object_or_404(Location, pk=site_id)
    site_kwargs = {
        'district' if location.level == 'district' else 'spray_area': location
    }
    results = {}
    for survey in surveys:
        queryset = Sample.objects.filter(visit=survey,
                                         **site_kwargs).exclude(household_id='0101466')
        if location.level == 'district':
            fields = ('spray_area__name', 'spray_area_id')
        else:
            fields = ('household_id', 'household_id')
        hh_per_district = queryset.values(*fields)\
            .distinct()\
            .annotate(houses_reached=Count('household_id', distinct=True))\
            .order_by(fields[0])
        row = OrderedDict(
            sorted(
                {
                    rec[fields[0]]: {
                        'houses_reached': rec['houses_reached'],
                        'location_id': rec[fields[1]],
                    }
                    for rec in hh_per_district
                }.items(),
                key=lambda t: t[0]))
        prokopacks = get_samples_for_method(queryset, Sample.PROKOPACK,
                                            'prokopack', fields[0])
        row = _merge_results_by_district(row, prokopacks, 'prokopack',
                                         fields[0])
        light_traps = get_samples_for_method(queryset, Sample.CDC_LIGHT_TRAP,
                                             'light_trap', fields[0])
        row = _merge_results_by_district(row, light_traps, 'light_trap',
                                         fields[0])

        results[survey] = {
            'rows': row,
            'totals': [
                hh_per_district.aggregate(
                    total_houses_reached=Sum('houses_reached')),
                prokopacks.aggregate(total_prokopacks=Sum('prokopack')),
                light_traps.aggregate(total_light_traps=Sum('light_trap')),
            ]
        }  # yapf: disable

    response = {}
    for i, j in results.items():
        for a, b in j['rows'].items():  # pylint: disable=invalid-name
            if 'light_trap' not in b:
                b['light_trap'] = 0
            if 'prokopack' not in b:
                b['prokopack'] = 0
            try:
                response[a].update({i: b})
            except KeyError:
                response[a] = {i: b}
            response[a][i].update({'totals': j['totals']})

    response = OrderedDict(sorted(response.items(), key=lambda t: t[0]))
    level = 'Site' if location.level == 'ta' else location.level.title()

    return render(request, 'trials/index.html', {
        'results': response,
        'surveys': surveys,
        'trials': True,
        'level': get_level(level),
        'title': "%s: %s" % (level, location.name)
    })


def get_level(level):
    """Returns the level below the level specified, defaults to District.
    """
    if level.lower() == 'district':
        return 'Site'
    elif level.lower() == 'ta' or level.lower() == 'site':
        return 'Household'

    return 'District'
