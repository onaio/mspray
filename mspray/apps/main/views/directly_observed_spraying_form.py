from django.db import connection

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError

from mspray.apps.main.models import (
    DirectlyObservedSprayingForm, SprayOperator
)
from mspray.apps.main.serializers.sprayday import (
    DirectlyObservedSprayingFormSerializer
)


class DirectlyObservedSprayingFormViewSet(viewsets.ModelViewSet):
    queryset = DirectlyObservedSprayingForm.objects.all()
    serializer_class = DirectlyObservedSprayingFormSerializer

    def create(self, request, *args, **kwargs):
        try:
            spray_operator_code = request.data.get('sprayop_code_name')
            DirectlyObservedSprayingForm.objects.create(
                correct_removal=request.data.get('correct_removal'),
                correct_mix=request.data.get('correct_mix'),
                rinse=request.data.get('rinse'),
                PPE=request.data.get('PPE'),
                CFV=request.data.get('CFV'),
                correct_covering=request.data.get('correct_covering'),
                leak_free=request.data.get('leak_free'),
                correct_distance=request.data.get('correct_distance'),
                correct_speed=request.data.get('correct_speed'),
                correct_overlap=request.data.get('correct_overlap'),
                district=request.data.get('district'),
                health_facility=request.data.get('health_facility'),
                supervisor_name=request.data.get('supervisor_name'),
                sprayop_code_name=spray_operator_code,
                tl_code_name=request.data.get('tl_code_name'),
                data=request.data,
                spray_date=request.data.get('today'),
            )

            self.calculate_average_spray_quality_score(spray_operator_code)
        except Exception as e:
            raise ParseError(e)

        return Response("Successfully created", status=status.HTTP_201_CREATED)

    def get_avg_quality_score_dict(self, sop_code):
        """
        retrieves the average quality score dictionary based
        - return: {'2012-1-1': '10',
                   '2015-10-1': '5'}
            """
        cursor = connection.cursor()

        sql_statement = """
select
    spray_date,
    sum(column_a_yes)+sum(column_b_yes)+sum(column_c_yes)+sum(column_d_yes)
    +sum(column_e_yes)+sum(column_f_yes)+sum(column_g_yes)+sum(column_h_yes)
    +sum(column_i_yes)+sum(column_j_yes) as yes
from
    (select
        spray_date,
        sum(case when correct_removal = 'yes' then 1 else 0 end) column_a_yes,
        sum(case when correct_mix = 'yes' then 1 else 0 end) column_b_yes,
        sum(case when rinse = 'yes' then 1 else 0 end) column_c_yes,
        sum(case when "PPE" = 'yes' then 1 else 0 end) column_d_yes,
        sum(case when "CFV" = 'yes' then 1 else 0 end) column_e_yes,
        sum(case when correct_covering = 'yes' then 1 else 0 end) column_f_yes,
        sum(case when leak_free = 'yes' then 1 else 0 end) column_g_yes,
        sum(case when correct_distance = 'yes' then 1 else 0 end) column_h_yes,
        sum(case when correct_speed = 'yes' then 1 else 0 end) column_i_yes,
        sum(case when correct_overlap = 'yes' then 1 else 0 end) column_j_yes
    from
        main_directlyobservedsprayingform
    where
        main_directlyobservedsprayingform.sprayop_code_name = '{sop_code}'
    group by
        spray_date) as filtered_directlyobservedsprayingform
group by spray_date;
""".format(**{'sop_code': sop_code})

        cursor.execute(sql_statement)

        queryset = cursor.cursor.fetchall()

        return {
            # spraydate: number of 'yes'
            a[0]: int(a[1].to_eng_string())
            for a in queryset
        }

    def calculate_average_spray_quality_score(self, spray_operator_code):
        avg_quality_score_dict = self.get_avg_quality_score_dict(
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
