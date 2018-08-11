# -*- coding: utf-8 -*-
"""Trials views"""
import json
from collections import OrderedDict

from django.conf import settings
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location, Household
from mspray.apps.main.query import get_location_qs
from mspray.apps.main.serializers.household import HouseholdBSerializer
from mspray.apps.main.serializers.target_area import (GeoTargetAreaSerializer,
                                                      TargetAreaQuerySerializer,
                                                      TargetAreaSerializer,
                                                      count_duplicates,
                                                      get_duplicates)
from mspray.apps.main.utils import get_location_dict, parse_spray_date
from mspray.apps.main.views.target_area import (TargetAreaHouseholdsViewSet,
                                                TargetAreaViewSet)
from mspray.apps.trials.models import Sample
from mspray.apps.trials.serializers import GeoSamplesSerializer

NOT_SPRAYABLE_VALUE = settings.NOT_SPRAYABLE_VALUE


def get_level(level):
    """Returns the level below the level specified, defaults to District.
    """
    if level.lower() == 'district':
        return 'Site'
    elif level.lower() == 'ta' or level.lower() == 'site':
        return 'Household'

    return 'District'


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
                        'location_id': rec['district_id'],
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

    return render(
        request, 'trials/index.html', {
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
        queryset = Sample.objects.filter(
            visit=survey, **site_kwargs).exclude(household_id='0101466')
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

    return render(
        request, 'trials/index.html', {
            'results': response,
            'surveys': surveys,
            'trials': True,
            'level': get_level(level),
            'title': "%s: %s" % (level, location.name),
            'location': location,
        })


class SiteMapView(SiteNameMixin, DetailView):  # pylint: disable=R0901
    """Site Map view"""
    template_name = 'trials/map.html'
    model = Location
    slug_field = 'pk'

    def get_queryset(self):
        queryset = super(SiteMapView, self).get_queryset()

        return get_location_qs(queryset)

    def get_context_data(self, **kwargs):
        context = super(SiteMapView, self).get_context_data(**kwargs)
        serializer_class = TargetAreaQuerySerializer \
            if settings.SITE_NAME == 'namibia' else TargetAreaSerializer
        location = context['object']
        if location.level == 'RHC':
            location = get_location_qs(
                Location.objects.filter(pk=location.pk), 'RHC').first()
        serializer = serializer_class(
            location, context={
                'request': self.request
            })
        context['target_data'] = serializer.data
        spray_date = parse_spray_date(self.request)
        if spray_date:
            context['spray_date'] = spray_date
        if settings.MSPRAY_SPATIAL_QUERIES or \
                context['object'].geom is not None:
            view = TargetAreaViewSet.as_view({'get': 'retrieve'})
            response = view(
                self.request, pk=context['object'].pk, format='geojson')
            response.render()
            context['not_sprayable_value'] = NOT_SPRAYABLE_VALUE
            context['ta_geojson'] = response.content
            bgeom = settings.HH_BUFFER and settings.OSM_SUBMISSIONS

            if self.object.level in ['district', 'RHC']:
                data = GeoTargetAreaSerializer(
                    get_location_qs(self.object.location_set.all(),
                                    self.object.level),
                    many=True,
                    context={
                        'request': self.request
                    }).data
                context['hh_geojson'] = json.dumps(data)
            else:
                loc = context['object']
                hhview = TargetAreaHouseholdsViewSet.as_view({
                    'get': 'retrieve'
                })
                response = hhview(
                    self.request,
                    pk=loc.pk,
                    bgeom=bgeom,
                    spray_date=spray_date,
                    format='geojson')
                response.render()
                hh_data = HouseholdBSerializer(
                    Household.objects.filter(location=loc), many=True,
                    context={'request': self.request}).data
                context['hh_geojson'] = json.dumps(hh_data)
                sprayed_duplicates = list(
                    get_duplicates(loc, True, spray_date))
                not_sprayed_duplicates = list(
                    get_duplicates(loc, False, spray_date))
                context['sprayed_duplicates_data'] = json.dumps(
                    sprayed_duplicates)
                context['sprayed_duplicates'] = count_duplicates(
                    loc, True, spray_date)
                context['not_sprayed_duplicates_data'] = json.dumps(
                    not_sprayed_duplicates)
                context['not_sprayed_duplicates'] = \
                    count_duplicates(loc, False)
                samples_data = GeoSamplesSerializer(
                    Sample.objects.filter(spray_area=location)
                    .distinct('household_id'),
                    many=True, context={'request': self.request}).data
                context['samples_geojson'] = json.dumps(samples_data)

        context['districts'] = Location.objects.filter(parent=None)\
            .values_list('id', 'code', 'name').order_by('name')

        context.update({'map_menu': True})
        context.update(get_location_dict(self.object.pk))
        context['not_sprayed_reasons'] = json.dumps(
            settings.MSPRAY_UNSPRAYED_REASON_OTHER)
        context['trials'] = True

        return context
