# -*- coding: utf-8 -*-
"""Trials views"""
from collections import OrderedDict

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import Cast
from django.shortcuts import render

from mspray.apps.trials.models import Sample


def get_samples_for_method(queryset, collection_method, key):
    """Return the queryset with the sam of tot_mosq for a given
    collection_method.
    """
    params = {key: Sum(Cast(KeyTextTransform('tot_mosq', 'data'),
                            models.IntegerField()))}
    return queryset.filter(collection_method=collection_method)\
        .values('district__name').distinct().order_by('district__name')\
        .annotate(**params)


def _merge_results_by_district(results, iter_data, key):
    """Return merges data represented by key in iter_data to the results
    dictionary.
    """
    for row in iter_data:
        try:
            results[row['district__name']].update({key: row[key]})
        except KeyError:
            results[row['district__name']] = {key: row[key]}

    return results


def index(request):
    """Index view"""
    surveys = Sample.objects.values_list(
        'visit', flat=True).order_by('visit').distinct()
    results = {}
    for survey in surveys:
        queryset = Sample.objects.filter(visit=survey)
        hh_per_district = Sample.objects.filter(visit=survey)\
            .values('district__name').distinct()\
            .annotate(houses_reached=Count('household_id', distinct=True))\
            .order_by('district__name')
        row = OrderedDict(sorted({
            rec['district__name']: {'houses_reached': rec['houses_reached']}
            for rec in hh_per_district
        }.items(), key=lambda t: t[0]))
        aspirators = get_samples_for_method(queryset, Sample.PROKOPACK,
                                            'aspirator')
        row = _merge_results_by_district(row, aspirators, 'aspirator')
        light_traps = get_samples_for_method(queryset, Sample.CDC_LIGHT_TRAP,
                                             'light_trap')
        row = _merge_results_by_district(row, light_traps, 'light_trap')


        results[survey] = {
            'rows': row,
            'totals': [
                hh_per_district.aggregate(
                    total_houses_reached=Sum('houses_reached')),
                aspirators.aggregate(total_aspirators=Sum('aspirator')),
                light_traps.aggregate(total_light_traps=Sum('light_trap')),
            ]
        }  # yapf: disable

    print(results)
    return render(request, 'trials/index.html', {
        'results': results,
        'surveys': surveys,
        'trials': True
    })
