# from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import render_to_response
from mspray.apps.main.models import TargetArea, District, SprayDay


def calculate(numerator, denominator, percentage):
    coverage = numerator/denominator
    if coverage > percentage:
        return 1

    return 0


def update_sprayed_structures(spray_points_sprayed, sprayed_structures):
    # set structures sprayed per day per spray operator
    for a in spray_points_sprayed:
        date_sprayed = a.data.get('today')
        spray_operator = a.data.get('sprayed/sprayop_name')
        key = "%s-%s" % (date_sprayed, spray_operator)
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
    for a in dist_hse:
        # a - {'district_name': '', 'houses': }
        target_areas = TargetArea.objects.filter(
                        targeted=TargetArea.TARGETED_VALUE,
                        district_name=a.get('district_name')).order_by(
                      'ranks', 'houses')

        sprayed_structures = {}
        target_areas_found_total = 0
        target_areas_sprayed_total = 0
        structures_sprayed_totals = 0
        for target_area in target_areas:
            structures = 1 if target_area.houses < 1 else target_area.houses
            spray_day = SprayDay.objects.filter(
                geom__coveredby=target_area.geom)
            # found
            spray_points_founds = spray_day.filter(
                data__contains='"sprayable_structure":"yes"').count()
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
        a['found'] = target_areas_found_total
        a['found_percentage'] = round((
            a.get('found') / target_areas.count()) * 100, 1)
        a['sprayed'] = target_areas_sprayed_total
        a['sprayed_percentage'] = round(
            (a.get('sprayed') / target_areas.count()) * 100, 1)
        a['sprayed_total'] = structures_sprayed_totals
        a['sprayed_total_percentage'] = round(
            (structures_sprayed_totals / a.get('houses') * 100), 1)
        a['target_areas'] = target_areas.count()

    return render_to_response('performance.html', {'data': dist_hse})


def get_total(spray_day, condition):
    if spray_day:
        if condition == "sprayable":
            queryset = spray_day.filter(
                data__contains='"sprayable_structure":"yes"')
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
                    district_name=district_name).order_by(
                  'ranks', 'houses')

    rows = {}
    for target_area in target_areas:
        spray_day = SprayDay.objects.filter(geom__coveredby=target_area.geom)

        for a in spray_day:
            if not rows.get(a.data.get('team_leader')):
                rows[a.data.get('team_leader')] = {
                    'sprayable': 0,
                    'not_sprayable': 0,
                    'sprayed': 0,
                    'refused': 0,
                    'other': 0,
                    'not_sprayed_total': 0,
                    'spray_success_rate': 0,
                    'team_leader': 0
                }

                team_leader_dict = rows.get(a.data.get('team_leader'))
                team_leader_dict['sprayable'] += get_total(
                    spray_day, "sprayable")
                team_leader_dict['not_sprayable'] += get_total(
                    spray_day, "not_sprayable")
                team_leader_dict['sprayed'] += get_total(spray_day, "sprayed")
                team_leader_dict['refused'] += get_total(spray_day, "refused")
                team_leader_dict['other'] += get_total(spray_day, "other")
                team_leader_dict['not_sprayed_total'] += team_leader_dict['other'] + team_leader_dict['refused']
                team_leader_dict['spray_success_rate'] += team_leader_dict['sprayable'] / 1 if team_leader_dict['sprayed'] == 0 else team_leader_dict['sprayed']
                
                rows[a.data.get('team_leader')] = team_leader_dict

    #return "Success!"
    return render_to_response('team-leaders.html', {'data': rows})
