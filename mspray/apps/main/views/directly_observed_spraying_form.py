from django.db import connection
from django.views.generic import ListView

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.renderers import TemplateHTMLRenderer

from mspray.apps.main.models import (
    DirectlyObservedSprayingForm, SprayOperator, Location
)
from mspray.apps.main.serializers.sprayday import (
    DirectlyObservedSprayingFormSerializer
)
from mspray.apps.main.utils import add_directly_observed_spraying_data


def get_directly_observed_spraying_data(column):
    cursor = connection.cursor()

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
group by
    {column};
""".format(**{'column': column})  # noqa

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
        avg_quality_score_dict = self.get_directly_observed_spraying_data(
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

    def get_district_data(self, districts, directly_observed_spraying_data):
        data = {}
        for a in districts:
            code = str(a.get('code'))
            name = a.get('name')

            records = directly_observed_spraying_data.get(code)
            if records:
                data[name] = {
                    'correct_removal': records[0],
                    'correct_mix': records[1],
                    'rinse': records[2],
                    'ppe': records[3],
                    'cfv': records[4],
                    'correct_covering': records[5],
                    'leak_free': records[6],
                    'correct_distance': records[7],
                    'correct_speed': records[8],
                    'correct_overlap': records[9],
                    'code': code
                }
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

        return data

    def get_context_data(self, **kwargs):
        context = super(
            DirectlyObservedSprayingView, self
        ).get_context_data(
            **kwargs
        )
        context['directly_observed_spraying'] = True

        districts = Location.objects.filter(parent=None).values('name', 'code')
        directly_observed_spraying_data = get_directly_observed_spraying_data(
            'district'
        )

        context['data'] = self.get_district_data(
            districts, directly_observed_spraying_data
        )
        return context
