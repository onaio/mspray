from django.db.models import Count

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework import status

from mspray.apps.main.models import(
    SprayOperatorDailySummary, SprayPointView, SprayOperator
)
from mspray.apps.main.serializers.sprayday import SprayOperatorDailySerializer


class SprayOperatorDailyViewSet(viewsets.ModelViewSet):
    queryset = SprayOperatorDailySummary.objects.all()
    serializer_class = SprayOperatorDailySerializer

    def create(self, request, *args, **kwargs):
        try:
            spray_form_id = request.data.get('sprayformid')
            sprayed = request.data.get('sprayed')
            found = request.data.get('found')
            spray_operator_code = request.data.get('sprayop_code')
            SprayOperatorDailySummary.objects.create(
                spray_form_id=spray_form_id,
                sprayed=sprayed,
                found=found,
                sprayoperator_code=spray_operator_code,
                data=request.data,
            )
            self.calculate_data_quality_check(
                spray_form_id, spray_operator_code
            )
        except Exception as e:
            raise ParseError(e)

        return Response("Successfully created", status=status.HTTP_201_CREATED)

    def get_hh_submission(self, spray_form_id):
        hh_submission = SprayPointView.objects.filter(
            sprayformid=spray_form_id
        ).values(
            'sprayformid'
        ).annotate(
            sprayformid_count=Count('sprayformid'),
            sprayed_count=Count('was_sprayed')
        )

        return hh_submission and hh_submission.first() or {}

    def get_sop_submission(self, spray_form_id):
        sop_submission = SprayOperatorDailySummary.objects.filter(
            spray_form_id=spray_form_id
        ).values(
            'spray_form_id'
        ).annotate(
            found_count=Count('found'),
            sprayed_count=Count('sprayed')
        )

        return sop_submission and sop_submission.first() or {}

    def calculate_data_quality_check(self, spray_form_id, spray_operator_code):
        # from HH Submission form total submissions
        hh_submission_agg = self.get_hh_submission(spray_form_id)

        # from SOP Summary form
        sop_submission_aggregate = self.get_sop_submission(spray_form_id)

        sop_found_count = None
        if hh_submission_agg:
            hh_sprayformid_count = hh_submission_agg.get('sprayformid_count')
            hh_sprayed_count = hh_submission_agg.get('sprayed_count')

            sop_submission = sop_submission_aggregate.get(spray_form_id)
            if sop_submission:
                sop_found_count = sop_submission.get('found_count')
                sop_sprayed_count = sop_submission.get('sprayed_count')

        data_quality_check = False
        if sop_found_count is not None:
            # check HH Submission Form total submissions count is equal to
            # SOP Summary Form 'found' count and HH Submission Form
            # 'was_sprayed' count is equal to SOP Summary Form 'sprayed'
            # count and both checks should be based on 'sprayformid'
            data_quality_check = sop_found_count == hh_sprayformid_count\
                and sop_sprayed_count == hh_sprayed_count

        so = SprayOperator.objects.filter(code=spray_operator_code)[0]
        if so:
            # update spray operator
            so.data_quality_check = data_quality_check
            so.save()

            team_leader = so.team_leader
            if data_quality_check:
                # if data_quality_check is True, check if all data quality
                # values for the rest of the spray operators is true before
                # saving
                data_quality_check = all(
                    [
                        a.get('data_quality_check')
                        for a in team_leader.sprayoperator_set.values(
                            'data_quality_check'
                        )
                    ]
                )

            # update team leader
            team_leader.data_quality_check = data_quality_check
            team_leader.save()

            # update district
            district = team_leader.location
            if data_quality_check:
                data_quality_check = all(
                    [
                        a.get('data_quality_check')
                        for a in district.teamleader_set.values(
                            'data_quality_check'
                        )
                    ]
                )

            district.data_quality_check = data_quality_check
            district.save()
