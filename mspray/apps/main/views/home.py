import csv
import json

from django.conf import settings
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.serializers.target_area import \
    GeoTargetAreaSerializer, get_duplicates, count_duplicates
from mspray.apps.main.serializers.target_area import DistrictSerializer
from mspray.apps.main.serializers.target_area import TargetAreaSerializer
from mspray.apps.main.serializers.target_area import TargetAreaQuerySerializer
from mspray.apps.main.views.target_area import TargetAreaViewSet
from mspray.apps.main.views.target_area import TargetAreaHouseholdsViewSet
from mspray.apps.main.utils import get_location_qs
from mspray.apps.main.utils import parse_spray_date
from mspray.apps.main.definitions import DEFINITIONS


def get_location_dict(code):
    data = {}
    if code:
        district = get_object_or_404(Location, pk=code)
        data['district'] = district
        data['district_code'] = district.pk
        data['district_name'] = district.name
        if district.level == settings.MSPRAY_TA_LEVEL:
            data['sub_locations'] = Location.objects\
                .filter(parent=district.parent)\
                .exclude(parent=None)\
                .values('id', 'level', 'name', 'parent')\
                .order_by('name')
            data['locations'] = Location.objects\
                .filter(parent=district.parent.parent)\
                .exclude(parent=None)\
                .values('id', 'level', 'name', 'parent')\
                .order_by('name')
        else:
            data['sub_locations'] = district.location_set.all()\
                .values('id', 'level', 'name', 'parent')\
                .order_by('name')
            data['locations'] = Location.objects\
                .filter(parent=district.parent)\
                .exclude(parent=None)\
                .values('id', 'level', 'name', 'parent')\
                .order_by('name')
        data['top_level'] = Location.objects.filter(parent=None)\
            .values('id', 'level', 'name', 'parent')\
            .order_by('name')
    if 'top_level' not in data:
        data['locations'] = Location.objects.filter(parent=None)\
            .values('id', 'level', 'name', 'parent')\
            .order_by('name')
    data['ta_level'] = settings.MSPRAY_TA_LEVEL
    data['higher_level_map'] = settings.HIGHER_LEVEL_MAP

    return data


class DistrictView(SiteNameMixin, ListView):
    template_name = 'home/district.html'
    model = Location
    slug_field = 'pk'

    def get_queryset(self):
        qs = super(DistrictView, self).get_queryset()
        pk = self.kwargs.get(self.slug_field)
        if pk is not None:
            qs = qs.filter(parent__pk=pk)
        else:
            qs = qs.filter(parent=None).order_by('name')

        return get_location_qs(qs)

    def get_context_data(self, **kwargs):
        context = super(DistrictView, self).get_context_data(**kwargs)
        qs = context['object_list'].extra(select={
            "xmin": 'ST_xMin("main_location"."geom")',
            "ymin": 'ST_yMin("main_location"."geom")',
            "xmax": 'ST_xMax("main_location"."geom")',
            "ymax": 'ST_yMax("main_location"."geom")'
        }).values(
            'pk', 'code', 'level', 'name', 'parent', 'structures',
            'xmin', 'ymin', 'xmax', 'ymax', 'num_of_spray_areas',
            'num_new_structures', 'total_structures', 'visited', 'sprayed'
        )
        pk = self.kwargs.get(self.slug_field)
        if pk is None:
            serializer_class = DistrictSerializer
        else:
            level = self.object_list.first().level \
                if self.object_list.first() else ''
            if level == 'RHC':
                serializer_class = DistrictSerializer
            else:
                serializer_class = TargetAreaQuerySerializer \
                    if settings.SITE_NAME == 'namibia' \
                    else TargetAreaSerializer
        serializer = serializer_class(qs, many=True,
                                      context={'request': self.request})
        context['district_list'] = serializer.data
        fields = ['structures', 'visited_total', 'visited_sprayed',
                  'visited_not_sprayed', 'visited_refused', 'visited_other',
                  'not_visited', 'found', 'num_of_spray_areas']
        totals = {}
        for rec in serializer.data:
            for field in fields:
                totals[field] = rec[field] + (totals[field]
                                              if field in totals else 0)
        district_code = self.kwargs.get(self.slug_field)
        context.update(get_location_dict(district_code))
        context['district_totals'] = totals
        if not district_code:
            context.update(DEFINITIONS['district'])
        else:
            loc = context.get('district')
            level = 'RHC' if loc.level == 'district' else 'ta'
            context.update(DEFINITIONS[level])

        return context


class TargetAreaView(SiteNameMixin, DetailView):
    template_name = 'home/map.html'
    model = Location
    slug_field = 'pk'

    def get_queryset(self):
        qs = super(TargetAreaView, self).get_queryset()

        return get_location_qs(qs)

    def get_context_data(self, **kwargs):
        context = super(TargetAreaView, self).get_context_data(**kwargs)
        serializer_class = TargetAreaQuerySerializer \
            if settings.SITE_NAME == 'namibia' else TargetAreaSerializer
        location = context['object']
        if location.level == 'RHC':
            location = get_location_qs(
                Location.objects.filter(pk=location.pk),
                'RHC'
            ).first()
        serializer = serializer_class(location,
                                      context={'request': self.request})
        context['target_data'] = serializer.data
        spray_date = parse_spray_date(self.request)
        if spray_date:
            context['spray_date'] = spray_date
        if settings.MSPRAY_SPATIAL_QUERIES or \
                context['object'].geom is not None:
            view = TargetAreaViewSet.as_view({'get': 'retrieve'})
            response = view(self.request, pk=context['object'].pk,
                            format='geojson')
            response.render()
            context['ta_geojson'] = response.content
            bgeom = settings.HH_BUFFER and settings.OSM_SUBMISSIONS

            if self.object.level in ['district', 'RHC']:
                data = GeoTargetAreaSerializer(
                    get_location_qs(self.object.location_set.all(),
                                    self.object.level),
                    many=True,
                    context={'request': self.request}
                ).data
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
                    format='geojson'
                )
                response.render()
                context['hh_geojson'] = response.content
                sprayed_duplicates = list(get_duplicates(loc, True))
                not_sprayed_duplicates = list(get_duplicates(loc, False))
                context['sprayed_duplicates_data'] = json.dumps(
                    sprayed_duplicates
                )
                context['sprayed_duplicates'] = count_duplicates(loc, True)
                context['not_sprayed_duplicates_data'] = json.dumps(
                    not_sprayed_duplicates
                )
                context['not_sprayed_duplicates'] = \
                    count_duplicates(loc, False)

        context['districts'] = Location.objects.filter(parent=None)\
            .values_list('id', 'code', 'name').order_by('name')

        context.update({'map_menu': True})
        context.update(get_location_dict(self.object.pk))

        return context


class SprayAreaView(SiteNameMixin, ListView):
    template_name = 'home/sprayareas.html'
    model = Location
    slug_field = 'pk'

    def get_queryset(self):
        qs = super(SprayAreaView, self).get_queryset()
        qs = qs.filter(level='ta')

        return get_location_qs(qs)

    def get_context_data(self, **kwargs):
        context = super(SprayAreaView, self).get_context_data(**kwargs)
        qs = context['object_list'].extra(select={
            "xmin": 'ST_xMin("main_location"."geom")',
            "ymin": 'ST_yMin("main_location"."geom")',
            "xmax": 'ST_xMax("main_location"."geom")',
            "ymax": 'ST_yMax("main_location"."geom")'
        }).values(
            'pk', 'code', 'level', 'name', 'parent', 'structures',
            'xmin', 'ymin', 'xmax', 'ymax', 'num_of_spray_areas',
            'num_new_structures', 'total_structures', 'parent__name',
            'parent__parent__name', 'parent__parent__pk', 'parent__pk'
        ).order_by('parent__parent__name', 'parent__name', 'name')
        if self.request.GET.get('format') != 'csv':
            serializer_class = TargetAreaSerializer
            serializer = serializer_class(qs, many=True,
                                          context={'request': self.request})
            context['district_list'] = serializer.data
        context['qs'] = qs
        # fields = ['structures', 'visited_total', 'visited_sprayed',
        #           'visited_not_sprayed', 'visited_refused', 'visited_other',
        #           'not_visited', 'found', 'num_of_spray_areas']
        # totals = {}
        # for rec in serializer.data:
        #     for field in fields:
        #         totals[field] = rec[field] + (totals[field]
        #                                       if field in totals else 0)
        context.update(get_location_dict(None))
        # context['district_totals'] = totals
        context.update(DEFINITIONS['ta'])

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'csv':
            def calc_percentage(numerator, denominator):
                try:
                    denominator = float(denominator)
                    numerator = float(numerator)
                except ValueError:
                    return ''

                if denominator == 0:
                    return ''

                return round((numerator * 100) / denominator)

            class SprayArea(object):
                def write(self, value):
                    return value

            def _data():
                yield [
                    "District",
                    "Health Centre",
                    "Spray Area",
                    "Structures on Ground",
                    "Found",
                    "Visited Sprayed",
                    "Spray Effectiveness",
                    "Found Coverage",
                    "Sprayed Coverage"
                ]
                for value in context.get('qs'):
                    district = TargetAreaSerializer(
                        value, context=context
                    ).data

                    yield [
                        district.get('district'),
                        district.get('rhc'),
                        district.get('district_name'),
                        district.get('structures'),
                        district.get('found'),
                        district.get('visited_sprayed'),
                        calc_percentage(district.get('visited_sprayed'),
                                        district.get('structures')),
                        calc_percentage(district.get('found'),
                                        district.get('structures')),
                        calc_percentage(district.get('visited_sprayed'),
                                        district.get('found'))
                    ]

            sprayarea_buffer = SprayArea()
            writer = csv.writer(sprayarea_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(row) for row in _data()),
                content_type='text/csv'
            )
            response['Content-Disposition'] = \
                'attachment; filename="sprayareas.csv"'

            return response

        return super(SprayAreaView, self).render_to_response(
            context, **response_kwargs
        )
