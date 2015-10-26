from datetime import datetime
from django.conf import settings
from django.db.models import Count, F, Sum
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import SprayPointView
from mspray.apps.main.models import SprayOperator
from mspray.apps.main.models import TeamLeader
from mspray.apps.main.utils import avg_time
from mspray.apps.main.utils import avg_time_tuple
from mspray.apps.main.utils import get_ta_in_location
from mspray.apps.main.utils import sprayable_queryset
from mspray.apps.main.utils import unique_spray_points
from mspray.apps.main.serializers.target_area import TargetAreaSerializer

HAS_SPRAYABLE_QUESTION = settings.HAS_SPRAYABLE_QUESTION
SPATIAL_QUERIES = settings.MSPRAY_SPATIAL_QUERIES
REASON_FIELD = settings.MSPRAY_UNSPRAYED_REASON_FIELD
REASON_REFUSED = settings.MSPRAY_UNSPRAYED_REASON_REFUSED
REASONS = settings.MSPRAY_UNSPRAYED_REASON_OTHER.copy()
REASONS.pop(REASON_REFUSED)
REASON_OTHER = REASONS.keys()
WAS_SPRAYED_FIELD = settings.MSPRAY_WAS_SPRAYED_FIELD
SPRAY_OPERATOR_NAME = settings.MSPRAY_SPRAY_OPERATOR_NAME
SPRAY_OPERATOR_CODE = settings.MSPRAY_SPRAY_OPERATOR_CODE
TEAM_LEADER_CODE = settings.MSPRAY_TEAM_LEADER_CODE
TEAM_LEADER_NAME = settings.MSPRAY_TEAM_LEADER_NAME


def calculate(numerator, denominator, percentage):
    if denominator == 0:
        return 0

    coverage = numerator/denominator

    if coverage > percentage:
        return 1

    return 0


def update_sprayed_structures(spray_points_sprayed, sprayed_structures,
                              per_so=True):
    # set structures sprayed per day per spray operator
    for a in spray_points_sprayed:
        date_sprayed = a.data.get('today')
        if per_so:
            spray_operator = a.data.get(SPRAY_OPERATOR_CODE)
            key = "%s-%s" % (date_sprayed, spray_operator)
        else:
            key = date_sprayed
        if sprayed_structures.get(key):
            sprayed_structures[key] = sprayed_structures[key] + 1
        else:
            sprayed_structures[key] = 1

    return sprayed_structures


class IsPerformanceViewMixin(SiteNameMixin):
    def get_context_data(self, **kwargs):
        context = super(IsPerformanceViewMixin, self)\
            .get_context_data(**kwargs)
        context['performance_tables'] = True

        return context


class DefinitionAndConditionView(IsPerformanceViewMixin, TemplateView):
    template_name = 'definitions-and-conditions.html'


class DistrictPerfomanceView(IsPerformanceViewMixin, ListView):
    model = Location
    template_name = 'performance.html'

    def get_queryset(self):
        qs = super(DistrictPerfomanceView, self).get_queryset()

        return qs.filter(parent=None).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(DistrictPerfomanceView, self)\
            .get_context_data(**kwargs)
        districts = Location.objects.filter(parent=None).annotate(
            num_target_area=Count('location'),
            total_structures=Sum('location__structures')
        )
        structures_found_by_district = Location.objects.filter(parent=None)\
            .values('name').filter(districts__sprayable_structure='yes')\
            .annotate(k=Count('districts', distinct=True))
        totals = {
            'avg_structures_per_user_per_so': 0,
            'found': 0,
            'found_gt_20': 0,
            'structures_found': 0,
            'sprayed': 0,
            'sprayed_total': 0,
            'target_areas': 0,
            'houses': 0
        }
        start_times = []
        end_times = []
        results = []
        for district in districts:
            target_areas = Location.objects.filter(parent=district)\
                .order_by('name')
            result = {'location': district}
            sprayed_structures = {}
            target_areas_found_total = 0
            target_areas_sprayed_total = 0
            structures_sprayed_totals = 0
            spray_points_total = 0
            found_gt_20 = 0
            ta_pks = list(get_ta_in_location(district))
            qs = sprayable_queryset(
                unique_spray_points(
                    SprayDay.objects.filter(location__pk__in=ta_pks)
                )
            )

            pks = list(qs.values_list('id', flat=True))
            _end_time = avg_time(pks, 'start')
            result['avg_end_time'] = _end_time
            end_times.append(_end_time)

            _start_time = avg_time(pks, 'end')
            result['avg_start_time'] = _start_time
            start_times.append(_start_time)

            sprayed_per_spray_operator_per_day = qs.extra(
                where=['data->>%s = %s'], params=[WAS_SPRAYED_FIELD, 'yes']
            ).values_list('location__code')\
                .annotate(a=Count('spray_operator'),
                          b=Count(Concat(F('spray_date'),
                                         F('spray_operator__code')),
                                  distinct=True))\
                .values_list('location__code', 'a', 'b')
            sprayed_structures = {}
            for t, a, b in sprayed_per_spray_operator_per_day:
                sprayed_structures[t] = (a, b)

            serializer = TargetAreaSerializer(target_areas, many=True)
            for target_area in serializer.data:
                structures = target_area['structures']
                structures = 0 if structures < 0 else structures
                # found
                spray_points_founds = target_area['found']
                spray_points_total += spray_points_founds

                if spray_points_founds > 0:
                    target_areas_found_total += calculate(spray_points_founds,
                                                          structures, 0.95)
                    found_gt_20 += calculate(spray_points_founds, structures,
                                             0.20)

                # sprayed
                spray_points_sprayed_count = target_area['visited_sprayed']
                if spray_points_sprayed_count > 0:
                    target_areas_sprayed_total += calculate(
                        spray_points_sprayed_count, structures, 0.85)
                    structures_sprayed_totals += spray_points_sprayed_count

            # calcuate Average structures sprayed per day per spray operator
            denominator = sum([b for a, b in sprayed_structures.values()])
            numerator = sum([a for a, b in sprayed_structures.values()])
            avg_struct_per_user_per_so = round(numerator/denominator) \
                if numerator != 0 else 0

            result['avg_structures_per_user_per_so'] = \
                avg_struct_per_user_per_so
            totals['avg_structures_per_user_per_so'] += \
                avg_struct_per_user_per_so

            result['found'] = target_areas_found_total
            totals['found'] += target_areas_found_total
            result['found_gt_20'] = found_gt_20
            totals['found_gt_20'] += found_gt_20

            result['found_percentage'] = round((
                target_areas_found_total / target_areas.count()) * 100, 0)
            result['structures_found'] = spray_points_total
            totals['structures_found'] += spray_points_total
            result['found_gt_20_percentage'] = round((
                found_gt_20 / target_areas.count()) * 100, 0)

            result['sprayed'] = target_areas_sprayed_total
            totals['sprayed'] += target_areas_sprayed_total

            result['sprayed_percentage'] = round(
                (target_areas_sprayed_total / target_areas.count()) * 100, 0)
            result['sprayed_total'] = structures_sprayed_totals
            totals['sprayed_total'] += structures_sprayed_totals

            if spray_points_total > 0:
                result['sprayed_total_percentage'] = round(
                    (structures_sprayed_totals / spray_points_total * 100), 0)
            result['target_areas'] = target_areas.count()
            totals['target_areas'] += target_areas.count()

            totals['houses'] += district.structures
            results.append(result)

        if totals['target_areas'] > 0:
            totals['found_percentage'] = round((
                totals['found']/totals['target_areas']) * 100)
            totals['found_gt_20_percentage'] = round((
                totals['found_gt_20']/totals['target_areas']) * 100)
            totals['sprayed_percentage'] = round((
                totals['sprayed']/totals['target_areas']) * 100)
            if totals['structures_found'] > 0:
                totals['sprayed_total_percentage'] = round((
                    totals['sprayed_total'] / totals['structures_found'])
                    * 100)
            totals['avg_structures_per_user_per_so'] = round(
                totals['avg_structures_per_user_per_so']/districts.count())

            if len(start_times) and len(end_times):
                totals['avg_start_time'] = avg_time_tuple(start_times)
                totals['avg_end_time'] = avg_time_tuple(end_times)

        context.update({
            'data': results, 'totals': totals
        })

        return context


def get_totals(spraypoints, condition):
    if condition == "sprayable":
        resultset = dict(spraypoints.annotate(c=Count('data')))
    elif condition == "non-sprayable":
        resultset = dict(spraypoints.extra(
            where=['data->>%s = %s'],
            params=['sprayable_structure', 'no']).annotate(
                c=Count('data')))
    elif condition == "sprayed":
        resultset = dict(spraypoints
                         .extra(where=['data->>%s = %s'],
                                params=[WAS_SPRAYED_FIELD, 'yes'])
                         .annotate(c=Count('data')))
    elif condition == "refused":
        resultset = dict(
            spraypoints.extra(
                where=['data->>%s = %s'],
                params=[REASON_FIELD, REASON_REFUSED]).annotate(
                    c=Count('data')))
    elif condition == "other":
        resultset = dict(
            spraypoints.extra(
                where=["data->>%s IN ({})".format(
                    ",".join(["'{}'".format(i) for i in REASON_OTHER]))],
                params=[REASON_FIELD]).annotate(c=Count('data')))

    return resultset


class TeamLeadersPerformanceView(IsPerformanceViewMixin, DetailView):
    model = Location
    slug_field = 'code'
    template_name = 'team-leaders.html'

    def get_context_data(self, **kwargs):
        context = super(TeamLeadersPerformanceView, self)\
            .get_context_data(**kwargs)
        district = context['object']

        data = []
        totals = {
            'avg_structures_per_user_per_so': 0,
            'other': 0,
            'refused': 0,
            'sprayed': 0,
            'sprayable': 0,
            'not_sprayable': 0,
            'not_sprayed_total': 0,
            'spray_success_rate': 0
        }

        ta_pks = list(get_ta_in_location(district))
        spraypoints_qs = unique_spray_points(
            SprayDay.objects.filter(location__pk__in=ta_pks)
        )
        spraypoints = spraypoints_qs.values_list('team_leader__code')
        non_sprayable = get_totals(spraypoints, "non-sprayable")
        spraypoints = sprayable_queryset(spraypoints)
        spraypoints_qs = sprayable_queryset(spraypoints_qs)
        sprayable = dict(
            spraypoints.annotate(c=Count('data'))
        )
        sprayed = get_totals(spraypoints, "sprayed")
        refused = get_totals(spraypoints, "refused")
        other = get_totals(spraypoints, "other")
        team_leaders = spraypoints.filter(team_leader__location=district)\
            .values_list(
                'team_leader__code', 'team_leader__name'
            ).distinct()

        start_times = []
        end_times = []
        sprayed_per_spray_operator_per_day = spraypoints.select_related()\
            .extra(
            where=['data->>%s = %s'], params=[WAS_SPRAYED_FIELD, 'yes']
        ).values_list('team_leader__code')\
            .annotate(a=Count('spray_operator'),
                      b=Count(Concat(F('spray_date'),
                                     F('spray_operator__code')),
                              distinct=True))\
            .values_list('team_leader__code', 'a', 'b')
        sprayed_structures = {}
        for t, a, b in sprayed_per_spray_operator_per_day:
            sprayed_structures[t] = (a, b)
        for team_leader, team_leader_name in team_leaders:
            qs = spraypoints_qs.extra(where=["data->>%s =  %s"],
                                      params=[TEAM_LEADER_CODE, team_leader])
            numerator = sprayed.get(team_leader, 0)
            denominator = 1 if sprayable.get(team_leader, 0) == 0 \
                else sprayable.get(team_leader)
            sprayed_success_rate = round((numerator/denominator) * 100, 1)

            numerator, denominator = sprayed_structures.get(team_leader,
                                                            (0, 1))
            denominator = 1 if denominator == 0 else denominator
            avg_structures_per_user_per_so = round(numerator/denominator)

            not_sprayed_total = refused.get(team_leader, 0) + \
                other.get(team_leader, 0)

            pks = list(qs.values_list('id', flat=True))
            _end_time = avg_time(pks, 'start')
            end_times.append(_end_time)

            _start_time = avg_time(pks, 'end')
            start_times.append(_start_time)

            data.append({
                'team_leader': team_leader,
                'team_leader_name': team_leader_name,
                'sprayable': sprayable.get(team_leader, 0),
                'not_sprayable': non_sprayable.get(team_leader, 0),
                'sprayed': sprayed.get(team_leader, 0),
                'refused': refused.get(team_leader, 0),
                'other': other.get(team_leader, 0),
                'spray_success_rate': sprayed_success_rate,
                'avg_structures_per_user_per_so':
                avg_structures_per_user_per_so,
                'not_sprayed_total': not_sprayed_total,
                'avg_start_time': _start_time,
                'avg_end_time': _end_time
            })

            # calculate totals
            totals['sprayable'] += sprayable.get(team_leader, 0)
            totals['not_sprayable'] += non_sprayable.get(team_leader, 0)
            totals['sprayed'] += sprayed.get(team_leader, 0)
            totals['refused'] += refused.get(team_leader, 0)
            totals['other'] += other.get(team_leader, 0)
            totals['not_sprayed_total'] += not_sprayed_total
            totals['avg_structures_per_user_per_so'] += \
                avg_structures_per_user_per_so

        # calculate spray_success_rate total
        numerator = totals['sprayed']
        denominator = 1 if totals['sprayable'] == 0 \
            else totals['sprayable']
        sprayed_success_rate = round((numerator/denominator) * 100, 1)
        totals['spray_success_rate'] = sprayed_success_rate

        if len(team_leaders):
            # calculate avg_structures_per_user_per_so total
            totals['avg_structures_per_user_per_so'] = round(
                totals['avg_structures_per_user_per_so']/len(team_leaders))

        if len(start_times) and len(end_times):
            totals['avg_start_time'] = avg_time_tuple(start_times)
            totals['avg_end_time'] = avg_time_tuple(end_times)

        context.update({
            'data': data,
            'totals': totals,
            'district': district,
            'district_name': district.name
        })

        return context


class SprayOperatorSummaryView(IsPerformanceViewMixin, DetailView):
    template_name = 'spray-operator-summary.html'
    model = Location
    slug_field = 'code'

    def get_context_data(self, **kwargs):
        data = []
        totals = {
            'no_of_days_worked': 0,
            'avg_structures_per_so': 0,
            'other': 0,
            'refused': 0,
            'sprayed': 0,
            'sprayable': 0,
            'not_sprayable': 0,
            'not_sprayed_total': 0,
            'spray_success_rate': 0
        }
        context = super(SprayOperatorSummaryView, self)\
            .get_context_data(**kwargs)
        district = context['object']
        team_leader = self.kwargs.get('team_leader')
        ta_pks = get_ta_in_location(district)
        spraypoints_qs = unique_spray_points(
            SprayDay.objects.filter(location__pk__in=ta_pks)
        )
        spraypoints_qs = spraypoints_qs.extra(
            select={'spray_operator_code': 'data->>%s'},
            select_params=[SPRAY_OPERATOR_CODE],
            where=['(data->%s) IS NOT NULL', "data->>%s =  %s"],
            params=[SPRAY_OPERATOR_CODE, "team_leader", team_leader]
        )
        spraypoints = spraypoints_qs.values_list('spray_operator_code')
        non_sprayable = get_totals(spraypoints, "non-sprayable")
        spraypoints = sprayable_queryset(spraypoints)
        spraypoints_qs = sprayable_queryset(spraypoints_qs)

        sprayable = get_totals(spraypoints, "sprayable")
        sprayed = get_totals(spraypoints, "sprayed")
        refused = get_totals(spraypoints, "refused")
        other = get_totals(spraypoints, "other")

        spray_operators = spraypoints.extra(
            select={
                "spray_operator_name": "(select name from main_sprayoperator"
                " where code = (data->>'{}'))".format(SPRAY_OPERATOR_CODE)
            }
        ).values_list('spray_operator_code', 'spray_operator_name')\
            .order_by('spray_operator_code').distinct()
        start_times = []
        end_times = []

        for spray_operator_code, spray_operator_name in spray_operators:
            qs = spraypoints_qs.extra(
                where=["data->>%s = %s"],
                params=[SPRAY_OPERATOR_CODE, spray_operator_code]
            )
            numerator = sprayed.get(spray_operator_code)
            denominator = 1 if sprayable.get(spray_operator_code) == 0 \
                else sprayable.get(spray_operator_code)
            spray_success_rate = round((numerator/denominator) * 100, 1)

            # calcuate Average structures sprayed per day per SO
            spray_points_sprayed = qs.extra(
                where=["data->>%s = %s"],
                params=[WAS_SPRAYED_FIELD, "yes"]
            )
            sprayed_structures = update_sprayed_structures(
                spray_points_sprayed, {}, per_so=False)
            no_of_days_worked = len(sprayed_structures.keys())

            denominator = 1 if no_of_days_worked == 0 else no_of_days_worked
            numerator = sum(a for a in sprayed_structures.values())
            avg_structures_per_so = round(numerator/denominator)

            not_sprayed_total = refused.get(spray_operator_code, 0) + \
                other.get(spray_operator_code, 0)

            pks = list(qs.values_list('id', flat=True))
            _end_time = avg_time(pks, 'start')
            end_times.append(_end_time)
            _start_time = avg_time(pks, 'end')
            start_times.append(_start_time)

            data.append({
                'spray_operator_code': spray_operator_code,
                'spray_operator_name': spray_operator_name,
                'sprayable': sprayable.get(spray_operator_code, 0),
                'not_sprayable': non_sprayable.get(spray_operator_code, 0),
                'sprayed': sprayed.get(spray_operator_code, 0),
                'refused': refused.get(spray_operator_code, 0),
                'other': other.get(spray_operator_code, 0),
                'no_of_days_worked': no_of_days_worked,
                'spray_success_rate': spray_success_rate,
                'avg_structures_per_so': avg_structures_per_so,
                'not_sprayed_total': not_sprayed_total,
                'avg_start_time': _start_time,
                'avg_end_time': _end_time
            })

            # totals
            totals['sprayed'] += sprayed.get(spray_operator_code, 0)
            totals['sprayable'] += sprayable.get(spray_operator_code, 0)
            totals['not_sprayable'] += \
                non_sprayable.get(spray_operator_code, 0)
            totals['refused'] += refused.get(spray_operator_code, 0)
            totals['other'] += other.get(spray_operator_code, 0)
            totals['not_sprayed_total'] += not_sprayed_total
            totals['no_of_days_worked'] += no_of_days_worked
            totals['avg_structures_per_so'] += avg_structures_per_so

        numerator = totals['sprayed']
        denominator = 1 if totals['sprayable'] == 0 else totals['sprayable']
        sprayed_success_rate = round((numerator / denominator) * 100, 1)
        totals['spray_success_rate'] = sprayed_success_rate

        if len(list(spray_operators)) != 0:
            totals['avg_structures_per_so'] = round(
                totals['avg_structures_per_so'] / len(list(spray_operators))
            )

        totals['avg_start_time'] = avg_time_tuple(start_times)
        totals['avg_end_time'] = avg_time_tuple(end_times)

        context.update(
            {
                'data': data,
                'totals': totals,
                'team_leader': team_leader,
                'team_leader_name':
                get_object_or_404(TeamLeader, code=team_leader).name,
                'district': district,
                'district_name': district.name
            }
        )

        return context


class SprayOperatorDailyView(IsPerformanceViewMixin, DetailView):
    template_name = 'spray-operator-daily.html'
    model = Location
    slug_field = 'code'

    def get_context_data(self, **kwargs):
        data = []
        totals = {
            'other': 0,
            'refused': 0,
            'sprayed': 0,
            'sprayable': 0,
            'not_sprayable': 0,
            'not_sprayed_total': 0,
            'spray_success_rate': 0
        }
        context = super(SprayOperatorDailyView, self)\
            .get_context_data(**kwargs)
        district = context['object']
        ta_pks = get_ta_in_location(district)
        spraypoints_qs = unique_spray_points(
            SprayDay.objects.filter(location__pk__in=ta_pks)
        )

        team_leader = self.kwargs.get('team_leader')
        spray_operator = self.kwargs.get('spray_operator')
        spraypoints = spraypoints_qs.extra(
            select={'today': 'data->>%s'}, select_params=['today'],
            where=["data->>%s =  %s", "data->>%s =  %s"],
            params=["team_leader", team_leader, SPRAY_OPERATOR_CODE,
                    spray_operator]
        ).values_list('today')

        non_sprayable = get_totals(spraypoints, "non-sprayable")
        spraypoints = sprayable_queryset(spraypoints)

        sprayable = get_totals(spraypoints, "sprayable")
        sprayed = get_totals(spraypoints, "sprayed")
        refused = get_totals(spraypoints, "refused")
        other = get_totals(spraypoints, "other")
        dates = sorted(spraypoints.values_list('today', flat=True).distinct())
        start_times = []
        end_times = []

        for index, _date in enumerate(dates):
            numerator = sprayed.get(_date, 0)
            denominator = 1 if sprayable.get(_date) == 0 \
                else sprayable.get(_date, 1)
            spray_success_rate = round((numerator/denominator) * 100, 1)

            not_sprayed_total = refused.get(_date, 0) + \
                other.get(_date, 0)

            qs = spraypoints.extra(where=["data->>%s = %s"],
                                   params=["today", _date])
            pks = list(qs.values_list('id', flat=True))
            _end_time = avg_time(pks, 'start')
            end_times.append(_end_time)
            _start_time = avg_time(pks, 'end')
            start_times.append(_start_time)

            data.append({
                'day': index + 1,
                'date': datetime.strptime(_date, '%Y-%m-%d'),
                'sprayable': sprayable.get(_date, 0),
                'not_sprayable': non_sprayable.get(_date, 0),
                'sprayed': sprayed.get(_date, 0),
                'refused': refused.get(_date, 0),
                'other': other.get(_date, 0),
                'spray_success_rate': spray_success_rate,
                'not_sprayed_total': not_sprayed_total,
                'avg_start_time': _start_time,
                'avg_end_time': _end_time
            })

            # calculate totals
            totals['sprayed'] += sprayed.get(_date, 0)
            totals['sprayable'] += sprayable.get(_date, 0)
            totals['not_sprayable'] += non_sprayable.get(_date, 0)
            totals['refused'] += refused.get(_date, 0)
            totals['other'] += other.get(_date, 0)
            totals['not_sprayed_total'] += not_sprayed_total

        numerator = totals['sprayed']
        denominator = 1 if totals['sprayable'] == 0 else totals['sprayable']
        sprayed_success_rate = round((numerator/denominator) * 100, 1)
        totals['spray_success_rate'] = sprayed_success_rate
        totals['avg_start_time'] = avg_time_tuple(start_times)
        totals['avg_end_time'] = avg_time_tuple(end_times)
        totals['avg_sprayed'] = 0
        if len(dates) != 0:
            totals['avg_sprayed'] = round(numerator / len(dates))

        context.update(
            {
                'data': data,
                'totals': totals,
                'spray_operator': spray_operator,
                'spray_operator_name':
                get_object_or_404(SprayOperator, code=spray_operator).name,
                'district': district,
                'district_name': district.name,
                'team_leader': team_leader,
                'team_leader_name':
                get_object_or_404(TeamLeader, code=team_leader).name,
            }
        )

        return context
