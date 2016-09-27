import json

from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.serializers.target_area import \
    GeoTargetAreaSerializer
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
            'num_new_structures', 'total_structures'
        )
        serializer_class = TargetAreaQuerySerializer \
            if settings.SITE_NAME == 'namibia' else TargetAreaSerializer
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


def get_duplicates(location, was_sprayed):
    return location.sprayday_set.filter(
        osmid__isnull=False, was_sprayed=was_sprayed
    ).values('osmid').annotate(
        dupes=Count('osmid')
    ).filter(dupes__gt=1)


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
                hhview = TargetAreaHouseholdsViewSet.as_view({
                    'get': 'retrieve'
                })
                response = hhview(
                    self.request,
                    pk=context['object'].pk,
                    bgeom=bgeom,
                    spray_date=spray_date,
                    format='geojson'
                )
                response.render()
                context['hh_geojson'] = response.content
                sprayed_duplicates = list(get_duplicates(
                    context['object'], True
                ))
                context['sprayed_duplicates_data'] = json.dumps(
                    sprayed_duplicates
                )
                context['sprayed_duplicates'] = len(sprayed_duplicates)
                context['not_sprayed_duplicates'] = len(
                    get_duplicates(context['object'], False)
                )

        context['districts'] = Location.objects.filter(parent=None)\
            .values_list('id', 'code', 'name').order_by('name')

        context.update({'map_menu': True})
        context.update(get_location_dict(self.object.pk))

        return context
