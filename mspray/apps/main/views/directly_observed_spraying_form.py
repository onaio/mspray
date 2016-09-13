from django.db import connection
from django.views.generic import ListView

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.renderers import TemplateHTMLRenderer

from mspray.apps.main.models import (
    DirectlyObservedSprayingForm, SprayOperator, Location, TeamLeader
)
from mspray.apps.main.serializers.sprayday import (
    DirectlyObservedSprayingFormSerializer
)
from mspray.apps.main.utils import add_directly_observed_spraying_data


def get_dos_data(column, where_params=None):
    cursor = connection.cursor()
    where_clause = ''

    if where_params:
        sub_column = where_params.get('column')
        value = where_params.get('value')
        where_clause = """
where
    main_directlyobservedsprayingform.{sub_column} = '{value}'
""".format(**{'sub_column': sub_column, 'value': value})

    sql_statement = """
select
    {column},
    sum(case when correct_removal = 'yes' then 1 else 0 end) correct_removal_yes,
    sum(case when correct_mix = 'yes' then 1 else 0 end) correct_mix_yes,
    sum(case when rinse = 'yes' then 1 else 0 end) rinse_yes,
    sum(case when "PPE" = 'yes' then 1 else 0 end) ppe_yes,
    sum(case when "CFV" = 'yes' then 1 else 0 end) cfv_yes,
    sum(case when correct_covering = 'yes' then 1 else 0 end) correct_covering_yes,
    sum(case when leak_free = 'yes' then 1 else 0 end) leak_free_yes,
    sum(case when correct_distance = 'yes' then 1 else 0 end) correct_distance_yes,
    sum(case when correct_speed = 'yes' then 1 else 0 end) correct_speed_yes,
    sum(case when correct_overlap = 'yes' then 1 else 0 end) correct_overlap_yes
from
    main_directlyobservedsprayingform
{where_clause}
group by
    {column};
""".format(**{'column': column, 'where_clause': where_clause})  # noqa

    cursor.execute(sql_statement)
    queryset = cursor.cursor.fetchall()

    return {
        a[0]: a[1:]
        for a in queryset
    }


class DirectlyObservedSprayingFormViewSet(viewsets.ModelViewSet):
    queryset = DirectlyObservedSprayingForm.objects.all()
    serializer_class = DirectlyObservedSprayingFormSerializer

    def create(self, request, *args, **kwargs):
        try:
            add_directly_observed_spraying_data(request.data)
        except Exception as e:
            raise ParseError(e)

        return Response("Successfully created", status=status.HTTP_201_CREATED)

    def calculate_average_spray_quality_score(self, spray_operator_code):
        avg_quality_score_dict = self.get_dos_data(
            spray_operator_code
        )

        yes_totals = sum([
            yes_total
            for spray_date, yes_total in avg_quality_score_dict.items()
        ])

        spray_date_totals = len(avg_quality_score_dict) or 1
        average_spray_quality_score = yes_totals / spray_date_totals
        so = SprayOperator.objects.filter(code=spray_operator_code)[0]
        if so:
            # update spray operator's average_spray_quality_score value
            so.average_spray_quality_score = average_spray_quality_score
            so.save()

            tl = so.team_leader
            spray_operators = tl.sprayoperator_set.values(
                'average_spray_quality_score'
            )

            # re-calculate and update average of team leader
            numerator = sum([
                a.get('average_spray_quality_score') for a in spray_operators
            ])
            denominator = spray_operators.count()
            average_spray_quality_score = numerator / denominator

            tl.average_spray_quality_score = average_spray_quality_score
            tl.save()

            # re-calculate and update average of district
            district = tl.location
            team_leaders = district.teamleader_set.values(
                'average_spray_quality_score'
            )
            numerator = sum([
                a.get('average_spray_quality_score') for a in team_leaders
            ])
            denominator = team_leaders.count()
            average_spray_quality_score = numerator / denominator

            district.average_spray_quality_score = average_spray_quality_score
            district.save()


class DirectlyObservedSprayingView(ListView):
    model = DirectlyObservedSprayingForm
    template_name = 'directly-observed-spraying.html'
    renderer_classes = (TemplateHTMLRenderer,)

    def get_data(self, user_list, directly_observed_spraying_data):
        data = {}
        totals = {
            'correct_removal': 0,
            'correct_mix': 0,
            'rinse': 0,
            'ppe': 0,
            'cfv': 0,
            'correct_covering': 0,
            'leak_free': 0,
            'correct_distance': 0,
            'correct_speed': 0,
            'correct_overlap': 0,
        }
        for a in user_list:
            code = str(a.get('code'))
            name = a.get('name')

            records = directly_observed_spraying_data.get(code)
            if records:
                correct_removal = records[0]
                correct_mix = records[1]
                rinse = records[2]
                ppe = records[3]
                cfv = records[4]
                correct_covering = records[5]
                leak_free = records[6]
                correct_distance = records[7]
                correct_speed = records[8]
                correct_overlap = records[9]

                data[name] = {
                    'correct_removal': correct_removal,
                    'correct_mix': correct_mix,
                    'rinse': rinse,
                    'ppe': ppe,
                    'cfv': cfv,
                    'correct_covering': correct_covering,
                    'leak_free': leak_free,
                    'correct_distance': correct_distance,
                    'correct_speed': correct_speed,
                    'correct_overlap': correct_overlap,
                    'code': code
                }

                totals['correct_removal'] += correct_removal
                totals['correct_mix'] += correct_mix
                totals['rinse'] += rinse
                totals['ppe'] += ppe
                totals['cfv'] += cfv
                totals['correct_covering'] += correct_covering
                totals['leak_free'] += leak_free
                totals['correct_distance'] += correct_distance
                totals['correct_speed'] += correct_speed
                totals['correct_overlap'] += correct_overlap
            else:
                data[name] = {
                    'correct_removal': 0,
                    'correct_mix': 0,
                    'rinse': 0,
                    'ppe': 0,
                    'cfv': 0,
                    'correct_covering': 0,
                    'leak_free': 0,
                    'correct_distance': 0,
                    'correct_speed': 0,
                    'correct_overlap': 0,
                    'code': code
                }

        for a, b in totals.items():
            totals[a] = round(
                b / len(user_list), 2
            )

        return data, totals

    def get_context_data(self, **kwargs):
        context = super(
            DirectlyObservedSprayingView, self
        ).get_context_data(
            **kwargs
        )
        context['directly_observed_spraying'] = True

        path = self.request.get_full_path()
        splitter = path.split('/')

        if len(splitter) == 3 and splitter[2] == '':
            districts = Location.objects.filter(
                parent=None
            ).values(
                'name', 'code'
            )
            directly_observed_spraying_data = get_dos_data('district')

            data, totals = self.get_data(
                districts, directly_observed_spraying_data
            )

            context['data'] = data
            context['totals'] = totals

        elif len(splitter) == 3:
            district_code = splitter[2]
            context['district_code'] = district_code

            team_leaders = TeamLeader.objects.filter(
                location__code=district_code
            ).values(
                'name', 'code'
            )

            directly_observed_spraying_data = get_dos_data(
                'tl_code_name', {'column': 'district', 'value': district_code}
            )

            data, totals = self.get_data(
                team_leaders, directly_observed_spraying_data
            )
            context['data'] = data
            context['totals'] = totals

        elif len(splitter) == 4:
            district_code = splitter[2]
            team_leader_code = splitter[3]
            context['district_code'] = district_code
            context['team_leader_code'] = team_leader_code

            spray_operators = SprayOperator.objects.filter(
                team_leader__code=team_leader_code
            ).values(
                'name', 'code'
            )

            directly_observed_spraying_data = get_dos_data(
                'sprayop_code_name',
                {'column': 'tl_code_name', 'value': team_leader_code}
            )

            data, totals = self.get_data(
                spray_operators, directly_observed_spraying_data
            )
            context['data'] = data
            context['totals'] = totals

        elif len(splitter) == 5:
            district_code = splitter[2]
            spray_operator_code = splitter[4]
            context['spray_operator_code'] = spray_operator_code

            directly_observed_spraying_data = get_dos_data(
                'spray_date',
                {'column': 'sprayop_code_name', 'value': spray_operator_code}
            )

            data = {}
            count = 1
            totals = {
                'correct_removal': 0,
                'correct_mix': 0,
                'rinse': 0,
                'ppe': 0,
                'cfv': 0,
                'correct_covering': 0,
                'leak_free': 0,
                'correct_distance': 0,
                'correct_speed': 0,
                'correct_overlap': 0,
            }
            for spray_date, records in directly_observed_spraying_data.items():
                if records:
                    correct_removal = records[0]
                    correct_mix = records[1]
                    rinse = records[2]
                    ppe = records[3]
                    cfv = records[4]
                    correct_covering = records[5]
                    leak_free = records[6]
                    correct_distance = records[7]
                    correct_speed = records[8]
                    correct_overlap = records[9]

                    data[spray_date] = {
                        'correct_removal': correct_removal,
                        'correct_mix': correct_mix,
                        'rinse': rinse,
                        'ppe': ppe,
                        'cfv': cfv,
                        'correct_covering': correct_covering,
                        'leak_free': leak_free,
                        'correct_distance': correct_distance,
                        'correct_speed': correct_speed,
                        'correct_overlap': correct_overlap,
                        'day': count
                    }

                    totals['correct_removal'] += correct_removal
                    totals['correct_mix'] += correct_mix
                    totals['rinse'] += rinse
                    totals['ppe'] += ppe
                    totals['cfv'] += cfv
                    totals['correct_covering'] += correct_covering
                    totals['leak_free'] += leak_free
                    totals['correct_distance'] += correct_distance
                    totals['correct_speed'] += correct_speed
                    totals['correct_overlap'] += correct_overlap
                    count = count + 1

            for a, b in totals.items():
                totals[a] = round(
                    b / len(directly_observed_spraying_data), 2
                )

            context['data'] = data
            context['totals'] = totals

        return context
