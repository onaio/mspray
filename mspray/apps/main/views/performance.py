from django.conf import settings
from django.db.models import Case, Count, F, Func, Sum, ExpressionWrapper, When
from django.db.models import Avg, FloatField, IntegerField
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from mspray.apps.main.mixins import SiteNameMixin
from mspray.apps.main.models import Location
from mspray.apps.main.models import SprayDay
from mspray.apps.main.models import SprayOperator
from mspray.apps.main.models import TeamLeaderAssistant
from mspray.apps.main.models import SprayOperatorDailySummary
from mspray.apps.main.utils import avg_time
from mspray.apps.main.utils import avg_time_tuple
from mspray.apps.main.utils import get_location_qs
from mspray.apps.main.utils import get_ta_in_location
from mspray.apps.main.utils import sprayable_queryset
from mspray.apps.main.utils import unique_spray_points
from mspray.apps.main.utils import not_sprayable_queryset
from mspray.apps.main.utils import sprayed_queryset
from mspray.apps.main.utils import refused_queryset
from mspray.apps.main.utils import other_queryset
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
TEAM_LEADER_ASSISTANT_CODE = getattr(
    settings, 'MSPRAY_TEAM_LEADER_ASSISTANT_CODE', 'tla_code'
)
TEAM_LEADER_NAME = settings.MSPRAY_TEAM_LEADER_NAME


def calculate(numerator, denominator, percentage):
    if denominator == 0:
        return 0

    coverage = numerator / denominator

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
        districts = Location.objects.filter(parent=None).order_by('name')
        results = []

        for district in districts:
            district_data, district_totals = get_district_data(district)
            district_totals.update({'location': district,
                                    'structures': district.structures})
            results.append(district_totals)

        district_count = districts.count()
        avg_start_time = avg_time_tuple([
            i.get('avg_start_time') for i in results if i.get('avg_start_time')
        ])
        avg_end_time = avg_time_tuple([
            i.get('avg_end_time') for i in results if i.get('avg_end_time')
        ])

        def _sum_key(a, b): return sum([i.get(a, 0) for i in b])

        totals = {
            'avg_start_time': avg_start_time,
            'avg_end_time': avg_end_time,
            'avg_structures_per_so': round(
                _sum_key('avg_structures_per_so', results) / district_count
            ),
            'sprayed': _sum_key('sprayed', results),
            'houses': _sum_key('structures', results),
            'sprayable': _sum_key('sprayable', results),
            'not_sprayable': _sum_key('not_sprayable', results),
            'refused': _sum_key('refused', results),
            'other': _sum_key('other', results),
            'not_sprayed_total': _sum_key('not_sprayed_total', results),
            'spray_success_rate': round(
                _sum_key('spray_success_rate', results) / district_count, 1
            ),
            'data_quality_check': any([i.get('data_quality_check')
                                       for i in results])
        }

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


def get_tla_data_quality_check(team_leader_assistant, spray_operator=None):
    data = dict(
        found_difference=[],
        sprayed_difference=[],
        data_quality_check=[]
    )
    qs = team_leader_assistant.sprayoperator_set.all()
    if spray_operator:
        qs = qs.filter(pk=spray_operator.pk)
    for spray_operator in qs:
        try:
            _date = spray_operator.sprayday_set.values_list(
                'spray_date', flat=True
            ).latest('spray_date')
        except SprayDay.DoesNotExist:
            pass
        else:
            if _date:
                sopdiff = get_spray_operator_data(spray_operator, _date)
                data['found_difference'].append(
                    sopdiff.get('found_difference')
                )
                data['sprayed_difference'].append(
                    sopdiff.get('sprayed_difference')
                )
                data['data_quality_check'].append(
                    sopdiff.get('data_quality_check')
                )

    return (
        sum(data.get('sprayed_difference')),
        sum(data.get('found_difference')),
        all(data.get('data_quality_check'))
    )


def get_district_data(district):
    data = []
    totals = {
        'avg_structures_per_so': 0,
        'other': 0,
        'refused': 0,
        'sprayed': 0,
        'sprayable': 0,
        'not_sprayable': 0,
        'not_sprayed_total': 0,
        'spray_success_rate': 0,
        'avg_quality_score': 0,
        'data_quality_check': True,
        'found_difference': 0,
        'sprayed_difference': 0
    }
    start_times = []
    end_times = []

    team_leaders = TeamLeaderAssistant.objects.filter(
        location=district
    ).order_by('name')

    for team_leader_assistant in team_leaders:
        k = get_tla_data(team_leader_assistant)[1]
        found_difference, sprayed_difference, data_quality_check = \
            get_tla_data_quality_check(team_leader_assistant)

        tla_code = team_leader_assistant.code
        tla_name = team_leader_assistant.name
        tla_not_sprayable = team_leader_assistant.sprayday_set.filter(
            data__contains={'osmstructure:spray_status': 'notsprayable'}
        ).count()
        tla_sprayable = k.get('sprayable')
        tla_sprayed = k.get('sprayed')
        tla_refused = k.get('refused')
        tla_other = k.get('other')
        tla_not_sprayed = k.get('not_sprayed_total')
        avg_structures_per_so = k.get('avg_structures_per_so')

        _end_time = k.get('avg_end_time') or (None, None)
        end_times.append(_end_time)
        _start_time = k.get('avg_start_time') or (None, None)
        start_times.append(_start_time)

        data.append({
            'team_leader': tla_code,
            'team_leader_name': tla_name,
            'sprayable': tla_sprayable,
            'not_sprayable': tla_not_sprayable,
            'sprayed': tla_sprayed,
            'refused': tla_refused,
            'other': tla_other,
            # 'no_of_days_worked': no_of_days_worked,
            'spray_success_rate': k.get('spray_success_rate'),
            'avg_structures_per_so': avg_structures_per_so,
            'not_sprayed_total': tla_not_sprayed,
            'avg_start_time': _start_time,
            'avg_end_time': _end_time,
            'data_quality_check': data_quality_check,
            'found_difference': found_difference,
            'sprayed_difference': sprayed_difference
        })

        # totals
        totals['sprayed'] += tla_sprayed
        totals['sprayable'] += tla_sprayable
        totals['not_sprayable'] += tla_not_sprayable
        totals['refused'] += tla_refused
        totals['other'] += tla_other
        totals['not_sprayed_total'] += tla_not_sprayed
        # totals['number_of_days_worked'] += no_of_days_worked
        totals['avg_structures_per_so'] += avg_structures_per_so
        if not data_quality_check:
            totals['data_quality_check'] = data_quality_check
        totals['found_difference'] += found_difference
        totals['sprayed_difference'] += sprayed_difference

    # calculate spray_success_rate total
    numerator = totals['sprayed']
    denominator = 1 if totals['sprayable'] == 0 \
        else totals['sprayable']
    sprayed_success_rate = round((numerator / denominator) * 100, 1)
    totals['spray_success_rate'] = sprayed_success_rate

    if len(team_leaders):
        # calculate avg_structures_per_user_per_so total
        totals['avg_structures_per_so'] = round(
            totals['avg_structures_per_so'] / len(team_leaders))
        totals['avg_quality_score'] = round(
            totals['avg_quality_score'] / len(list(team_leaders)), 2
        )

    if len(start_times) and len(end_times):
        totals['avg_start_time'] = avg_time_tuple(start_times)
        totals['avg_end_time'] = avg_time_tuple(end_times)

    return (data, totals)


class TeamLeadersPerformanceView(IsPerformanceViewMixin, DetailView):
    model = Location
    slug_field = 'id'
    template_name = 'team-leaders.html'

    def get_context_data(self, **kwargs):
        context = super(TeamLeadersPerformanceView, self)\
            .get_context_data(**kwargs)
        district = context['object']

        data, totals = get_district_data(district)

        context.update({
            'data': data,
            'totals': totals,
            'district': district,
            'district_name': district.name
        })

        return context


def get_sop_data(team_leader_assistant, spray_operator):
    return SprayOperator.objects.filter(
        team_leader_assistant=team_leader_assistant,
        pk=spray_operator.pk
    )\
        .values('team_leader_assistant')\
        .annotate(
            d_found=Count('sprayday'),
            d_sprayed=Sum(Case(
                When(sprayday__was_sprayed=True, then=1),
                default=0,
                output_field=IntegerField()
            )),
            d_not_sprayed=Sum(Case(
                When(sprayday__was_sprayed=False, then=1),
                default=0,
                output_field=IntegerField()
            )),
            d_refused=Sum(Case(When(
                sprayday__was_sprayed=False,
                sprayday__data__contains={
                    'osmstructure:notsprayed_reason': 'refused'
                }, then=1
            ), default=0, output_field=IntegerField())
            ),
            d_number_of_days_worked=Count('sprayday__spray_date',
                                          distinct=True)
        ).annotate(
            d_success_rate=Case(When(d_found__gt=0, then=ExpressionWrapper(
                F('d_sprayed') * 100 / Func(
                    F('d_found'), function='CAST',
                    template='%(function)s(%(expressions)s AS FLOAT)'
                ),
                FloatField()
            )), default=0, output_field=FloatField()),
            d_other=Case(When(d_not_sprayed__gt=0,
                              then=F('d_not_sprayed') - F('d_refused')),
                         default=0, output_field=IntegerField())
        )\
        .aggregate(
            found=Sum('d_found'),
            sprayed=Sum('d_sprayed'),
            not_sprayed=Sum('d_not_sprayed'),
            refused=Sum('d_refused'),
            number_of_days_worked=Sum('d_number_of_days_worked'),
            success_rate=Avg('d_success_rate'),
            other=Sum('d_other')
        )


def get_tla_data(team_leader_assistant):
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
        'spray_success_rate': 0,
        'data_quality_check': True,
        'found_difference': 0,
        'sprayed_difference': 0
    }
    start_times = []
    end_times = []

    sops = team_leader_assistant.sprayoperator_set.all().order_by('name')
    for spray_operator in sops:
        # spray_operator = SprayOperator.objects.get(pk=sop.get('pk'))
        sop = get_sop_data(team_leader_assistant, spray_operator)
        found_difference = sprayed_difference = 0
        found_difference, sprayed_difference, data_quality_check = \
            get_tla_data_quality_check(team_leader_assistant,
                                       spray_operator)

        sop_code = spray_operator.code
        sop_name = spray_operator.name
        sop_found = sop.get('found')
        sop_sprayed = sop.get('sprayed')
        sop_refused = sop.get('refused')
        sop_other = sop.get('other')
        sop_success_rate = sop.get('success_rate')
        sop_not_sprayed = sop.get('not_sprayed')
        no_of_days_worked = sop.get('number_of_days_worked')
        avg_structures_per_so = round(sop_found / no_of_days_worked) \
            if no_of_days_worked else 0
        qs = SprayDay.objects.filter(
            spray_operator_id=spray_operator.pk
        )
        pks = list(qs.values_list('id', flat=True))
        _end_time = avg_time(pks, 'start')
        end_times.append(_end_time)
        _start_time = avg_time(pks, 'end')
        start_times.append(_start_time)

        data.append({
            'spray_operator_code': sop_code,
            'spray_operator_name': sop_name,
            'sprayable': sop_found,
            'sprayed': sop_sprayed,
            'refused': sop_refused,
            'other': sop_other,
            'no_of_days_worked': sop.get('number_of_days_worked'),
            'spray_success_rate': round(sop_success_rate, 1),
            'avg_structures_per_so': avg_structures_per_so,
            'not_sprayed_total': sop_not_sprayed,
            'avg_start_time': _start_time,
            'avg_end_time': _end_time,
            'data_quality_check': data_quality_check,
            'found_difference': found_difference,
            'sprayed_difference': sprayed_difference
        })

        # totals
        totals['sprayed'] += sop_sprayed
        totals['sprayable'] += sop_found
        # totals['not_sprayable'] += \
        #     non_sprayable.get(sop_code, 0)
        totals['refused'] += sop_refused
        totals['other'] += sop_other
        totals['not_sprayed_total'] += sop_not_sprayed
        totals['no_of_days_worked'] += no_of_days_worked
        totals['avg_structures_per_so'] += avg_structures_per_so
        if not data_quality_check:
            totals['data_quality_check'] = data_quality_check
        totals['found_difference'] += found_difference
        totals['sprayed_difference'] += sprayed_difference

    numerator = totals['sprayed']
    denominator = 1 if totals['sprayable'] == 0 else totals['sprayable']
    sprayed_success_rate = round((numerator / denominator) * 100, 1)
    totals['spray_success_rate'] = sprayed_success_rate

    if len(sops):
        totals['avg_structures_per_so'] = round(
            totals['avg_structures_per_so'] / len(list(sops))
        )

    totals['avg_start_time'] = avg_time_tuple(start_times)
    totals['avg_end_time'] = avg_time_tuple(end_times)

    return (data, totals)


class SprayOperatorSummaryView(IsPerformanceViewMixin, DetailView):
    template_name = 'spray-operator-summary.html'
    model = Location
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super(SprayOperatorSummaryView, self)\
            .get_context_data(**kwargs)
        district = context['object']
        team_leader = self.kwargs.get('team_leader')
        team_leader_assistant = get_object_or_404(TeamLeaderAssistant,
                                                  code=team_leader)
        data, totals = get_tla_data(team_leader_assistant)

        context.update(
            {
                'data': data,
                'totals': totals,
                'team_leader': team_leader,
                'team_leader_name':
                get_object_or_404(TeamLeaderAssistant, code=team_leader).name,
                'district': district,
                'district_name': district.name
            }
        )

        return context


def get_formid(spray_operator, spray_date):
        return '%s.%s' % (spray_date.strftime('%d.%m'), spray_operator.code)


def get_spray_operator_data(spray_operator, spray_date):
    formid = get_formid(spray_operator, spray_date)
    sop = SprayOperator.objects.filter(
        code=spray_operator.code, sprayday__spray_date=spray_date
    )\
        .values('sprayday__spray_date')\
        .annotate(
            found=Count('sprayday'),
            sprayed=Sum(Case(
                When(sprayday__was_sprayed=True, then=1),
                default=0,
                output_field=IntegerField()
            )),
            sprayed_sprayformid=Sum(Case(
                When(
                    sprayday__was_sprayed=True,
                    sprayday__data__contains={'sprayformid': formid},
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )),
            not_sprayed=Sum(Case(
                When(sprayday__was_sprayed=False, then=1),
                default=0,
                output_field=IntegerField()
            )),
            refused=Sum(Case(When(
                sprayday__was_sprayed=False,
                sprayday__data__contains={
                    'osmstructure:notsprayed_reason': 'refused'
                }, then=1
            ), default=0, output_field=IntegerField())
            ),
            found_sprayformid=Sum(Case(When(
                sprayday__data__contains={'sprayformid': formid},
                then=1
            ), default=0, output_field=IntegerField())
            )
        ).annotate(
            success_rate=Case(When(found__gt=0, then=ExpressionWrapper(
                F('sprayed') * 100 / Func(
                    F('found'), function='CAST',
                    template='%(function)s(%(expressions)s AS FLOAT)'
                ),
                FloatField()
            )), default=0, output_field=FloatField()),
            other=Case(When(not_sprayed__gt=0,
                            then=F('not_sprayed') - F('refused')),
                       default=0, output_field=IntegerField())
        ).values(
            'pk', 'code', 'found', 'sprayed', 'refused', 'other',
            'not_sprayed', 'sprayday__spray_date', 'success_rate',
            'found_sprayformid', 'sprayed_sprayformid'
        ).first()

    sprayed_sprayformid = sop.get('sprayed_sprayformid')
    found_sprayformid = sop.get('found_sprayformid')

    formid = get_formid(spray_operator,  spray_date)
    summary = SprayOperatorDailySummary.objects.filter(
        sprayoperator_code=spray_operator.code,
        data__sprayformid=formid
    ).aggregate(
        r_found=Sum('found'),
        r_sprayed=Sum('sprayed')
    )

    r_found = summary.get('r_found') or 0
    r_sprayed = summary.get('r_sprayed') or 0

    found_difference = r_found - found_sprayformid
    sprayed_difference = r_sprayed - sprayed_sprayformid
    data_quality_check = r_found == found_sprayformid \
        and r_sprayed == sprayed_sprayformid

    data = dict()
    for k, v in sop.items():
        data[k] = v

    data['sop_found'] = r_found
    data['sop_sprayed'] = r_sprayed
    data['found_difference'] = found_difference
    data['sprayed_difference'] = sprayed_difference
    data['data_quality_check'] = data_quality_check

    return data


class SprayOperatorDailyView(IsPerformanceViewMixin, DetailView):
    template_name = 'spray-operator-daily.html'
    model = Location
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        data = []
        totals = {
            'other': 0,
            'refused': 0,
            'sprayed': 0,
            'sprayable': 0,
            'not_sprayable': 0,
            'not_sprayed_total': 0,
            'spray_success_rate': 0,
            'data_quality_check': True,
            'found_difference': 0,
            'sprayed_difference': 0

        }
        context = super(SprayOperatorDailyView, self)\
            .get_context_data(**kwargs)
        district = context['object']

        team_leader = self.kwargs.get('team_leader')
        spray_operator_code = self.kwargs.get('spray_operator')
        spray_operator = get_object_or_404(SprayOperator,
                                           code=spray_operator_code)
        dates = spray_operator.sprayday_set.values_list(
            'spray_date', flat=True
        ).distinct().order_by('spray_date')
        start_times = []
        end_times = []

        for index, _date in enumerate(dates):
            sop = get_spray_operator_data(spray_operator, _date)
            found = sop.get('found')
            sprayed = sop.get('sprayed')
            found_difference = sop.get('found_difference')
            sprayed_difference = sop.get('sprayed_difference')
            data_quality_check = sop.get('data_quality_check')
            qs = spray_operator.sprayday_set.filter(spray_date=_date)
            pks = list(qs.values_list('id', flat=True))
            _end_time = avg_time(pks, 'start')
            end_times.append(_end_time)
            _start_time = avg_time(pks, 'end')
            start_times.append(_start_time)

            data.append({
                'day': index + 1,
                'date': _date,
                'sprayable': found,
                'sprayed': sprayed,
                'refused': sop.get('refused'),
                'other': sop.get('other'),
                'spray_success_rate': round(
                    sop.get('success_rate'), 1),
                'not_sprayed_total': sop.get('not_sprayed'),
                'avg_start_time': _start_time,
                'avg_end_time': _end_time,
                'data_quality_check': data_quality_check,
                'found_difference': found_difference,
                'sprayed_difference': sprayed_difference
            })

            # calculate totals
            totals['sprayed'] += sop.get('sprayed')
            totals['sprayable'] += sop.get('found')
            totals['refused'] += sop.get('refused')
            totals['other'] += sop.get('other')
            totals['not_sprayed_total'] += sop.get('not_sprayed')
            if not data_quality_check:
                totals['data_quality_check'] = data_quality_check
            totals['found_difference'] += found_difference
            totals['sprayed_difference'] += sprayed_difference

        numerator = totals['sprayed']
        denominator = 1 if totals['sprayable'] == 0 else totals['sprayable']
        sprayed_success_rate = round((numerator / denominator) * 100, 1)
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
                'spray_operator': spray_operator.code,
                'spray_operator_name': spray_operator.name,
                'district': district,
                'district_name': district.name,
                'team_leader': team_leader,
                'team_leader_name': spray_operator.team_leader_assistant.name
            }
        )

        return context
