from collections import OrderedDict

from django.db.models import Count
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
from mspray.apps.main.utils import (
    add_directly_observed_spraying_data, get_dos_data
)


def calculate_percentage(numerator, denominator):
    return round((numerator / denominator) * 100, 2)


class DirectlyObservedSprayingFormViewSet(viewsets.ModelViewSet):
    queryset = DirectlyObservedSprayingForm.objects.all()
    serializer_class = DirectlyObservedSprayingFormSerializer

    def create(self, request, *args, **kwargs):
        try:
            add_directly_observed_spraying_data(request.data)
        except Exception as e:
            raise ParseError(e)

        return Response("Successfully created", status=status.HTTP_201_CREATED)


class DirectlyObservedSprayingView(ListView):
    model = DirectlyObservedSprayingForm
    template_name = 'directly-observed-spraying.html'
    renderer_classes = (TemplateHTMLRenderer,)

    def get_submission_count(self, kwargs):
        level = kwargs.get('level')
        filter_args = kwargs.get('filter-args')
        column = ''
        if level in ["spray-operator", "team-leader"]:
            columns = {
                "spray-operator": 'sprayop_code_name',
                "team-leader": 'tl_code_name'
            }
            column = columns.get(level)
            qs = DirectlyObservedSprayingForm.objects.filter(
                **filter_args
            ).values(
                column
            ).annotate(
                count=Count('sprayop_code_name')
            )

        elif level == "district":
            column = level
            qs = DirectlyObservedSprayingForm.objects.values(
                'district'
            ).annotate(
                count=Count('sprayop_code_name')
            )

        return {a.get(column): a.get('count') for a in qs}

    def get_data(self, user_list, directly_observed_spraying_data, kwargs):
        data = OrderedDict()
        average = {
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
            'total_yes': 0
        }
        total = {
            'submission_count': 0
        }

        def get_average_spray_quality_score(qs):
            return {
                a.get('code'): a.get('average_spray_quality_score')
                for a in qs
            }

        submissions_count = self.get_submission_count(kwargs)

        for a in user_list:
            code = str(a.get('code'))
            name = a.get('name')
            average_spray_quality_score = a.get('average_spray_quality_score')

            records = directly_observed_spraying_data.get(code)
            if records:
                submission_count = submissions_count.get(code)
                correct_removal = calculate_percentage(
                    records[0], submission_count)
                correct_mix = calculate_percentage(
                    records[1], submission_count)
                rinse = calculate_percentage(
                    records[2], submission_count)
                ppe = calculate_percentage(
                    records[3], submission_count)
                cfv = calculate_percentage(
                    records[4], submission_count)
                correct_covering = calculate_percentage(
                    records[5], submission_count)
                leak_free = calculate_percentage(
                    records[6], submission_count)
                correct_distance = calculate_percentage(
                    records[7], submission_count)
                correct_speed = calculate_percentage(
                    records[8], submission_count)
                correct_overlap = calculate_percentage(
                    records[9], submission_count)

                data[name] = {
                    'submission_count': submission_count,
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
                    'code': code,
                    'total_yes': average_spray_quality_score
                }

                average['correct_removal'] += correct_removal
                average['correct_mix'] += correct_mix
                average['rinse'] += rinse
                average['ppe'] += ppe
                average['cfv'] += cfv
                average['correct_covering'] += correct_covering
                average['leak_free'] += leak_free
                average['correct_distance'] += correct_distance
                average['correct_speed'] += correct_speed
                average['correct_overlap'] += correct_overlap
                average['total_yes'] += average_spray_quality_score
                total['submission_count'] += submission_count
            else:
                data[name] = {
                    'submission_count': 0,
                    'correct_removal': 0.0,
                    'correct_mix': 0.0,
                    'rinse': 0.0,
                    'ppe': 0.0,
                    'cfv': 0.0,
                    'correct_covering': 0.0,
                    'leak_free': 0.0,
                    'correct_distance': 0.0,
                    'correct_speed': 0.0,
                    'correct_overlap': 0.0,
                    'code': code,
                    'total_yes': 0.0
                }

        for a, b in average.items():
            average[a] = round(
                b / (len(user_list) or 1), 2
            )

        return data, average, total

    def spray_operator_daily_performance_handler(self, context, splitter):
        spray_operator_code = splitter[4]
        context['spray_operator_code'] = spray_operator_code

        directly_observed_spraying_data = get_dos_data(
            'spray_date',
            {'column': 'sprayop_code_name', 'value': spray_operator_code}
        )

        data = OrderedDict()
        count = 1
        average = {
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
            'avg_dos_score': 0,
            'total_yes': 0
        }

        total = {
            'submission_count': 0,
        }

        submissions_count = {
            a.get('spray_date'): a.get('count')
            for a in DirectlyObservedSprayingForm.objects.filter(
                sprayop_code_name=spray_operator_code
            ).values(
                'spray_date'
            ).annotate(
                count=Count('spray_date')
            )
        }

        for spray_date, records in directly_observed_spraying_data.items():
            if records:
                submission_count = submissions_count.get(spray_date)
                correct_removal = calculate_percentage(
                    records[0], submission_count)
                correct_mix = calculate_percentage(
                    records[1], submission_count)
                rinse = calculate_percentage(records[2], submission_count)
                ppe = calculate_percentage(records[3], submission_count)
                cfv = calculate_percentage(records[4], submission_count)
                correct_covering = calculate_percentage(
                    records[5], submission_count)
                leak_free = calculate_percentage(
                    records[6], submission_count)
                correct_distance = calculate_percentage(
                    records[7], submission_count)
                correct_speed = calculate_percentage(
                    records[8], submission_count)
                correct_overlap = calculate_percentage(
                    records[9], submission_count)
                total_yes = sum(records)

                data[spray_date] = {
                    'day': count,
                    'submission_count': submission_count,
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
                    'total_yes': total_yes
                }

                average['correct_removal'] += correct_removal
                average['correct_mix'] += correct_mix
                average['rinse'] += rinse
                average['ppe'] += ppe
                average['cfv'] += cfv
                average['correct_covering'] += correct_covering
                average['leak_free'] += leak_free
                average['correct_distance'] += correct_distance
                average['correct_speed'] += correct_speed
                average['correct_overlap'] += correct_overlap
                average['total_yes'] += total_yes
                total['submission_count'] += submission_count
                count = count + 1

        for a, b in average.items():
            average[a] = round(
                b / (len(directly_observed_spraying_data) or 1), 2
            )

        context['data'] = data
        context['average'] = average
        context['total'] = total

        return context

    def get_context_data(self, **kwargs):
        context = super(
            DirectlyObservedSprayingView, self
        ).get_context_data(
            **kwargs
        )
        context['directly_observed_spraying'] = True

        path = self.request.get_full_path()
        splitter = path.split('/')

        if len(splitter) == 2:
            districts = Location.objects.filter(
                parent=None
            ).values(
                'name', 'code', 'average_spray_quality_score'
            ).order_by('name')
            directly_observed_spraying_data = get_dos_data('district')

            kwargs = {
                'level': 'district'
            }
            data, average, total = self.get_data(
                districts, directly_observed_spraying_data, kwargs
            )
            context['data'] = data
            context['average'] = average
            context['total'] = total

        elif len(splitter) == 3:
            district_code = splitter[2]
            context['district_code'] = district_code

            team_leaders = TeamLeader.objects.filter(
                location__code=district_code
            ).values(
                'name', 'code', 'average_spray_quality_score'
            )

            directly_observed_spraying_data = get_dos_data(
                'tl_code_name', {'column': 'district', 'value': district_code}
            )

            kwargs = {
                'level': 'team-leader',
                'filter-args': {
                    'district': district_code
                }
            }
            data, average, total = self.get_data(
                team_leaders, directly_observed_spraying_data, kwargs
            )
            context['data'] = data
            context['average'] = average
            context['total'] = total

        elif len(splitter) == 4:
            district_code = splitter[2]
            team_leader_code = splitter[3]
            context['district_code'] = district_code
            context['team_leader_code'] = team_leader_code

            spray_operators = SprayOperator.objects.filter(
                team_leader__code=team_leader_code
            ).values(
                'name', 'code', 'average_spray_quality_score'
            )

            directly_observed_spraying_data = get_dos_data(
                'sprayop_code_name',
                {'column': 'tl_code_name', 'value': team_leader_code}
            )

            kwargs = {
                'level': 'spray-operator',
                'filter-args': {
                    'tl_code_name': team_leader_code
                }
            }
            data, average, total = self.get_data(
                spray_operators, directly_observed_spraying_data, kwargs
            )
            context['data'] = data
            context['average'] = average
            context['total'] = total

        elif len(splitter) == 5:
            context = self.spray_operator_daily_performance_handler(
                context, splitter
            )

        return context
