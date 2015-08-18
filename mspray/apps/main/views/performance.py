# from django.core.cache import cache
from django.db.models import Q, Count
from django.shortcuts import render_to_response
from mspray.apps.main.models import TargetArea, District, SprayDay


def calculate(numerator, denominator, percentage):
    coverage = numerator/denominator
    if coverage > percentage:
        return 1

    return 0


def update_sprayed_structures(
        spray_points_sprayed, sprayed_structures, per_so=True):
    # set structures sprayed per day per spray operator
    for a in spray_points_sprayed:
        date_sprayed = a.data.get('today')
        if per_so:
            spray_operator = a.data.get('sprayed/sprayop_name')
            key = "%s-%s" % (date_sprayed, spray_operator)
        else:
            key = date_sprayed
        if sprayed_structures.get(key):
            sprayed_structures[key] = sprayed_structures[key] + 1
        else:
            sprayed_structures[key] = 1

    return sprayed_structures


def definitions_and_conditions(request):
    return render_to_response('definitions-and-conditions.html')


def district(request):
    # get districts and the number of structures in them
    dist_hse = District.objects.filter().values('houses', 'district_name')
    totals = {
        'avg_structures_per_user_per_so': 0,
        'found': 0,
        'structures_found': 0,
        'sprayed': 0,
        'sprayed_total': 0,
        'target_areas': 0,
        'houses': 0
    }

    for a in dist_hse:
        # a - {'district_name': '', 'houses': }
        target_areas = TargetArea.objects.filter(
            targeted=TargetArea.TARGETED_VALUE,
            district_name=a.get('district_name')).order_by('ranks', 'houses')

        sprayed_structures = {}
        target_areas_found_total = 0
        target_areas_sprayed_total = 0
        structures_sprayed_totals = 0
        spray_points_total = 0
        for target_area in target_areas:
            structures = 1 if target_area.houses < 1 else target_area.houses
            spray_day = SprayDay.objects.filter(
                geom__coveredby=target_area.geom)
            # found
            spray_points_founds = spray_day.filter(
                data__contains='"sprayable_structure":"yes"').count()
            spray_points_total += spray_points_founds
            if spray_points_founds > 0:
                target_areas_found_total += calculate(spray_points_founds,
                                                      structures,
                                                      0.95)

            # sprayed
            spray_points_sprayed = spray_day.filter(
                data__contains='"sprayed/was_sprayed":"yes"')

            spray_points_sprayed_count = spray_points_sprayed.count()
            if spray_points_sprayed_count > 0:
                target_areas_sprayed_total += calculate(
                    spray_points_sprayed_count, structures, 0.85)
                structures_sprayed_totals += spray_points_sprayed_count

                # update sprayed structures
                sprayed_structures = update_sprayed_structures(
                    spray_points_sprayed, sprayed_structures)

        # calcuate Average structures sprayed per day per spray operator
        denominator = len(sprayed_structures.keys())
        numerator = sum(a for a in sprayed_structures.values())
        avg_struct_per_user_per_so = round(numerator/denominator, 1)

        a['avg_structures_per_user_per_so'] = avg_struct_per_user_per_so
        totals['avg_structures_per_user_per_so'] += avg_struct_per_user_per_so

        a['found'] = target_areas_found_total
        totals['found'] += target_areas_found_total

        a['found_percentage'] = round((
            a.get('found') / target_areas.count()) * 100, 0)
        a['structures_found'] = spray_points_total
        totals['structures_found'] += spray_points_total

        a['sprayed'] = target_areas_sprayed_total
        totals['sprayed'] += target_areas_sprayed_total

        a['sprayed_percentage'] = round(
            (a.get('sprayed') / target_areas.count()) * 100, 0)
        a['sprayed_total'] = structures_sprayed_totals
        totals['sprayed_total'] += structures_sprayed_totals

        a['sprayed_total_percentage'] = round(
            (structures_sprayed_totals / spray_points_total * 100), 0)
        a['target_areas'] = target_areas.count()
        totals['target_areas'] += target_areas.count()

        totals['houses'] += a.get('houses')

    totals['found_percentage'] = round((
        totals['found']/totals['target_areas']) * 100)
    totals['sprayed_percentage'] = round((
        totals['sprayed']/totals['target_areas']) * 100)
    totals['sprayed_total_percentage'] = round((
        totals['sprayed_total']/totals['structures_found']) * 100)
    totals['avg_structures_per_user_per_so'] = round(
        totals['avg_structures_per_user_per_so']/dist_hse.count(), 0)

    return render_to_response('performance.html',
                              {'data': dist_hse, 'totals': totals})


def get_total(spray_day, condition, spray_operator=None):
    if spray_day:
        if spray_operator:
            spray_day = spray_day.filter(
                data__contains='"sprayed/sprayop_name":"%s"' % spray_operator)
        if condition == "sprayable":
            queryset = spray_day.extra(
                where=["data->>%s = %s"],
                params=["sprayable_structure", "yes"]
            )
        elif condition == "not_sprayable":
            queryset = spray_day.filter(
                data__contains='"sprayable_structure":"no"')
        elif condition == "sprayed":
            queryset = spray_day.filter(
                data__contains='"sprayed/was_sprayed":"yes"')
        elif condition == "refused":
            queryset = spray_day.filter(
                data__contains='"unsprayed/reason":"Refused"')
        elif condition == "other":
            queryset = spray_day.filter(
                Q(data__contains='"unsprayed/reason":"Other"') |
                Q(data__contains='"unsprayed/reason":"Sick"') |
                Q(data__contains='"unsprayed/reason":"Funeral"') |
                Q(data__contains='"unsprayed/reason":"Locked"') |
                Q(data__contains='"unsprayed/reason":"No one home/Missed"'))

        return queryset.count()


def team_leaders(request, district_name):
    target_areas = TargetArea.objects.filter(
        targeted=TargetArea.TARGETED_VALUE,
        district_name=district_name).order_by('ranks', 'houses')

    rows = {}
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

    spraypoints = SprayDay.objects.filter(geom__coveredby=target_areas.collect()).extra(select={'team_leader':'data->>%s'}, select_params=['team_leader']).values_list('team_leader')
    sprayable_qs = spraypoints.extra(where=['data->>%s = %s'], params=['sprayable_structure', 'yes'])
    sprayable = dict(sprayable_qs.annotate(c=Count('data')))
    non_sprayable = dict(spraypoints.extra(where=['data->>%s = %s'], params=['sprayable_structure', 'no']).annotate(c=Count('data')))
    sprayed = dict(spraypoints.extra(where=['data->>%s = %s'], params=['sprayed/was_sprayed', 'yes']).annotate(c=Count('data')))
    refused = dict(spraypoints.extra(where=['data->>%s = %s'], params=['unsprayed/reason', 'Refused']).annotate(c=Count('data')))
    other = dict(spraypoints.extra(where=['data->>%s IN (%s, %s, %s, %s, %s)'], params=['unsprayed/reason', 'Other', 'Sick', 'Funeral', 'Locked', 'No one home/Missed']).annotate(c=Count('data')))
    team_leaders = spraypoints.values_list('team_leader', flat=True).distinct()

    for team_leader in team_leaders:
        numerator = sprayed.get(team_leader)
        denominator = 1 if sprayable.get(team_leader) == 0 \
            else sprayable.get(team_leader)
        sprayed_success_rate = round((numerator/denominator) * 100, 1)

        # calcuate Average structures sprayed per day per SO
        spray_points_sprayed = SprayDay.objects.filter(
            data__contains='"sprayed/was_sprayed":"yes"').filter(
            data__contains='"team_leader":"{}"'.format(team_leader))
        sprayed_structures = update_sprayed_structures(
            spray_points_sprayed, {})
        denominator = 1 if len(sprayed_structures.keys()) == 0 \
            else len(sprayed_structures.keys())
        numerator = sum(a for a in sprayed_structures.values())
        avg_structures_per_user_per_so = round(numerator/denominator, 1)

        not_sprayed_total = refused.get(team_leader) + other.get(team_leader)

        leader_dict = {
            'sprayable': sprayable.get(team_leader),
            'not_sprayable': non_sprayable.get(team_leader),
            'sprayed': sprayed.get(team_leader),
            'refused': refused.get(team_leader),
            'other': other.get(team_leader),
            'spray_success_rate': sprayed_success_rate,
            'avg_structures_per_user_per_so': avg_structures_per_user_per_so,
            'not_sprayed_total': not_sprayed_total
        }

        rows[team_leader] = leader_dict

        # calculate totals
        totals['sprayable'] += sprayable.get(team_leader)
        totals['not_sprayable'] += non_sprayable.get(team_leader)
        totals['sprayed'] += sprayed.get(team_leader)
        totals['refused'] += refused.get(team_leader)
        totals['other'] += other.get(team_leader)
        totals['not_sprayed_total'] += not_sprayed_total
        totals['avg_structures_per_user_per_so'] += \
            avg_structures_per_user_per_so

    # calculate spray_success_rate total
    numerator = totals['sprayed']
    denominator = 1 if totals['sprayable'] == 0 \
        else totals['sprayable']
    sprayed_success_rate = round((numerator/denominator) * 100, 1)
    totals['spray_success_rate'] = sprayed_success_rate

    # calculate avg_structures_per_user_per_so total
    totals['avg_structures_per_user_per_so'] = round(
        totals['avg_structures_per_user_per_so']/len(team_leaders), 0)

    return render_to_response('team-leaders.html',
                              {'data': rows,
                               'totals': totals,
                               'district_name': district_name})


def spray_operators(request, team_leader):
    spray_day = SprayDay.objects.filter(
        data__contains='"team_leader":"%s"' % team_leader)
    select = {'spray_operator': "data->>'sprayed/sprayop_name'"}
    spray_operators = spray_day.extra(
        select=select).values_list('spray_operator', flat=True).distinct()

    spray_operators_dict = {}
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
    for a in spray_operators:
        if a is not None:
            sprayed = get_total(spray_day, "sprayed", spray_operator=a)
            totals['sprayed'] += sprayed

            sprayable = get_total(spray_day, "sprayable", spray_operator=a)
            totals['sprayable'] += sprayable

            not_sprayable = get_total(
                spray_day, "not_sprayable", spray_operator=a)
            totals['not_sprayable'] += not_sprayable

            refused = get_total(spray_day, "refused", spray_operator=a)
            totals['refused'] += refused

            other = get_total(spray_day, "other", spray_operator=a)
            totals['other'] += other

            not_sprayed_total = other + refused
            totals['not_sprayed_total'] += not_sprayed_total

            numerator = sprayed
            denominator = 1 if sprayable == 0 else sprayable
            spray_success_rate = round((numerator/denominator) * 100, 0)
            totals['spray_success_rate'] += spray_success_rate

            # calcuate Average structures sprayed per day per SO
            spray_points_sprayed = spray_day.filter(
                data__contains='"sprayed/was_sprayed":"yes"').filter(
                data__contains='"sprayed/sprayop_name":"%s"' % a)
            sprayed_structures = update_sprayed_structures(
                spray_points_sprayed, {}, per_so=False)
            no_of_days_worked = len(sprayed_structures.keys())
            totals['no_of_days_worked'] += no_of_days_worked

            denominator = 1 if no_of_days_worked == 0 else no_of_days_worked
            numerator = sum(a for a in sprayed_structures.values())
            avg_structures_per_so = round(numerator/denominator, 1)
            totals['avg_structures_per_so'] += avg_structures_per_so

            spray_operators_dict[a] = {
                'no_of_days_worked': no_of_days_worked,
                'sprayed': sprayed,
                'sprayable': sprayable,
                'not_sprayable': not_sprayable,
                'refused': refused,
                'other': other,
                'not_sprayed_total': not_sprayed_total,
                'spray_success_rate': spray_success_rate,
                'avg_structures_per_so': avg_structures_per_so,
            }

    numerator = totals['sprayed']
    denominator = 1 if totals['sprayable'] == 0 else totals['sprayable']
    sprayed_success_rate = round((numerator/denominator) * 100, 1)
    totals['spray_success_rate'] = sprayed_success_rate

    spray_operators = [a for a in spray_operators if a is not None]
    totals['avg_structures_per_so'] = round(
        totals['avg_structures_per_so']/len(spray_operators), 1)

    return render_to_response('spray-operators.html',
                              {'data': spray_operators_dict,
                               'totals': totals,
                               'team_leader': team_leader})
